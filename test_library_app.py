"""Tests for library_app.py, run against a throwaway in-memory database so
they never touch the real library.db.

These exercise the behaviors that were missing from the original script:
  - borrow_item refuses to hand out an item that's already borrowed, and
    flips isBorrowed on when it succeeds (the column existed in the schema
    but the old code never read or wrote it).
  - return_item refuses to return a borrowId that doesn't belong to the
    customer asking, and flips isBorrowed back off when it succeeds.
  - prompt_int rejects non-numeric input instead of letting a typo silently
    match zero rows.
"""

import io
import sqlite3
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

import library_app as app

SCHEMA = """
CREATE TABLE item(
    itemId INTEGER PRIMARY KEY,
    type TEXT NOT NULL,
    title TEXT NOT NULL,
    author TEXT,
    isBorrowed BOOLEAN DEFAULT FALSE
);
CREATE TABLE customer(
    customerId INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    birthDate TEXT,
    address TEXT,
    email TEXT
);
CREATE TABLE borrow(
    borrowId INTEGER PRIMARY KEY,
    customerId INTEGER,
    dueDate TEXT,
    itemId INTEGER,
    FOREIGN KEY (customerId) REFERENCES customer(customerId),
    FOREIGN KEY (itemId) REFERENCES item(itemId)
);
CREATE TABLE event(
    eventId INTEGER PRIMARY KEY,
    name TEXT,
    date TEXT,
    roomId INTEGER,
    type TEXT
);
CREATE TABLE eventAttend(
    eventId INTEGER,
    customerId INTEGER,
    PRIMARY KEY (eventId, customerId)
);
CREATE TABLE employee(
    employeeId INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    position TEXT,
    startDate TEXT,
    salary REAL
);
"""


def make_db():
    conn = sqlite3.connect(":memory:")
    conn.executescript(SCHEMA)
    conn.executemany(
        "INSERT INTO item (itemId, type, title, author, isBorrowed) VALUES (?, ?, ?, ?, ?)",
        [
            (1, "Book", "Dune", "Frank Herbert", 0),
            (2, "Book", "Dune", "Frank Herbert", 1),  # a second, already-borrowed copy
        ],
    )
    conn.executemany(
        "INSERT INTO customer (customerId, name) VALUES (?, ?)",
        [(1, "Alice"), (2, "Ben")],
    )
    conn.commit()
    return conn


def run_silently(func, *args, **kwargs):
    """Call func with stdout suppressed, returning what it printed."""
    buf = io.StringIO()
    with redirect_stdout(buf):
        func(*args, **kwargs)
    return buf.getvalue()


class PromptIntTests(unittest.TestCase):
    def test_valid_number(self):
        with patch("builtins.input", return_value="5"):
            self.assertEqual(app.prompt_int("id: "), 5)

    def test_blank_cancels(self):
        with patch("builtins.input", return_value=""):
            self.assertIsNone(app.prompt_int("id: "))

    def test_rejects_non_numeric_then_accepts(self):
        with patch("builtins.input", side_effect=["abc", "7"]):
            self.assertEqual(app.prompt_int("id: "), 7)


class BorrowItemTests(unittest.TestCase):
    def setUp(self):
        self.conn = make_db()
        self.cur = self.conn.cursor()

    def tearDown(self):
        self.conn.close()

    def test_borrow_available_item_marks_it_borrowed(self):
        with patch("builtins.input", side_effect=["Dune", "1", "1"]):
            run_silently(app.borrow_item, self.cur)

        self.cur.execute("SELECT isBorrowed FROM item WHERE itemId = 1")
        self.assertEqual(self.cur.fetchone()[0], 1)

        self.cur.execute("SELECT customerId, itemId FROM borrow")
        self.assertEqual(self.cur.fetchall(), [(1, 1)])

    def test_cannot_borrow_an_already_borrowed_copy(self):
        # itemId 2 is already borrowed in make_db(); the only "Dune" offered
        # should be itemId 1, so asking for itemId 2 must be refused.
        with patch("builtins.input", side_effect=["Dune", "2", "1"]):
            output = run_silently(app.borrow_item, self.cur)

        self.assertIn("isn't one of the available items", output)
        self.cur.execute("SELECT COUNT(*) FROM borrow")
        self.assertEqual(self.cur.fetchone()[0], 0)

    def test_no_available_copies(self):
        self.cur.execute("UPDATE item SET isBorrowed = 1 WHERE itemId = 1")
        with patch("builtins.input", return_value="Dune"):
            output = run_silently(app.borrow_item, self.cur)
        self.assertIn("no available", output)


class ReturnItemTests(unittest.TestCase):
    def setUp(self):
        self.conn = make_db()
        self.cur = self.conn.cursor()
        # Alice (customerId 1) already has itemId 2 checked out.
        self.cur.execute(
            "INSERT INTO borrow (borrowId, customerId, dueDate, itemId) VALUES (1, 1, '2026-10-01', 2)"
        )
        self.conn.commit()

    def tearDown(self):
        self.conn.close()

    def test_owner_can_return_their_borrow(self):
        with patch("builtins.input", side_effect=["1", "1"]):
            run_silently(app.return_item, self.cur)

        self.cur.execute("SELECT COUNT(*) FROM borrow WHERE borrowId = 1")
        self.assertEqual(self.cur.fetchone()[0], 0)

        self.cur.execute("SELECT isBorrowed FROM item WHERE itemId = 2")
        self.assertEqual(self.cur.fetchone()[0], 0)

    def test_other_customer_cannot_return_someone_elses_borrow(self):
        # Ben (customerId 2) has no borrows of his own, so this should be
        # rejected rather than silently deleting Alice's borrow record.
        with patch("builtins.input", side_effect=["2"]):
            output = run_silently(app.return_item, self.cur)

        self.assertIn("don't have any borrowed items", output)
        self.cur.execute("SELECT COUNT(*) FROM borrow WHERE borrowId = 1")
        self.assertEqual(self.cur.fetchone()[0], 1)

    def test_cannot_return_a_borrow_id_that_isnt_yours(self):
        # A second customer with a borrow of their own tries to return
        # customer 1's borrowId by guessing the number.
        self.cur.execute(
            "INSERT INTO borrow (borrowId, customerId, dueDate, itemId) VALUES (2, 2, '2026-10-02', 1)"
        )
        self.conn.commit()

        with patch("builtins.input", side_effect=["2", "1"]):
            output = run_silently(app.return_item, self.cur)

        self.assertIn("isn't one of your borrowed items", output)
        self.cur.execute("SELECT COUNT(*) FROM borrow WHERE borrowId = 1")
        self.assertEqual(self.cur.fetchone()[0], 1)


class RunOneInstructionTests(unittest.TestCase):
    def setUp(self):
        self.conn = make_db()
        self.cur = self.conn.cursor()

    def tearDown(self):
        self.conn.close()

    def test_exit_code_stops_the_loop(self):
        self.assertFalse(app.run_one_instruction(self.cur, "0"))

    def test_unrecognized_code_keeps_looping(self):
        output = run_silently(app.run_one_instruction, self.cur, "99")
        self.assertIn("valid code", output)

    def test_find_item_dispatches(self):
        with patch("builtins.input", return_value="Dune"):
            output = run_silently(app.run_one_instruction, self.cur, "1")
        self.assertIn("Dune", output)


if __name__ == "__main__":
    unittest.main()
