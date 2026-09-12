"""Create library.db and populate it with sample data.

The README has always documented this as the second setup step
(`python setup_database.py`, right after `pip install -r requirements.txt`),
but the script itself was never committed -- anyone who cloned the repo
had a `library_app.py` with nowhere to point until they reverse-engineered
the schema from the code. This script builds the schema from scratch and
seeds it with enough sample rows that `library_app.py` is usable
immediately after setup.

Safe to re-run: it drops any existing tables first.
"""

import sqlite3

DB_PATH = "library.db"

SCHEMA = """
DROP TABLE IF EXISTS borrow;
DROP TABLE IF EXISTS eventAttend;
DROP TABLE IF EXISTS recommendAudience;
DROP TABLE IF EXISTS fine;
DROP TABLE IF EXISTS event;
DROP TABLE IF EXISTS room;
DROP TABLE IF EXISTS futureItem;
DROP TABLE IF EXISTS previousEmployee;
DROP TABLE IF EXISTS employee;
DROP TABLE IF EXISTS customer;
DROP TABLE IF EXISTS item;

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

CREATE TABLE fine(
    fineId INTEGER PRIMARY KEY,
    customerId INTEGER,
    amount REAL,
    FOREIGN KEY (customerId) REFERENCES customer(customerId)
);

CREATE TABLE room(
    roomId INTEGER PRIMARY KEY,
    type TEXT,
    capacity INTEGER
);

CREATE TABLE event(
    eventId INTEGER PRIMARY KEY,
    name TEXT,
    date TEXT,
    roomId INTEGER,
    type TEXT,
    FOREIGN KEY (roomId) REFERENCES room(roomId)
);

CREATE TABLE recommendAudience(
    eventId INTEGER,
    customerId INTEGER,
    PRIMARY KEY (eventId, customerId),
    FOREIGN KEY (eventId) REFERENCES event(eventId),
    FOREIGN KEY (customerId) REFERENCES customer(customerId)
);

CREATE TABLE eventAttend(
    eventId INTEGER,
    customerId INTEGER,
    PRIMARY KEY (eventId, customerId),
    FOREIGN KEY (eventId) REFERENCES event(eventId),
    FOREIGN KEY (customerId) REFERENCES customer(customerId)
);

CREATE TABLE employee(
    employeeId INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    position TEXT,
    startDate TEXT,
    salary REAL
);

CREATE TABLE previousEmployee(
    previousEmployeeId INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    position TEXT,
    startDate TEXT,
    endDate TEXT,
    salary REAL
);

CREATE TABLE futureItem(
    futureItemId INTEGER PRIMARY KEY,
    type TEXT,
    addDate TEXT,
    title TEXT,
    author TEXT
);

CREATE TABLE borrow(
    borrowId INTEGER PRIMARY KEY,
    customerId INTEGER,
    dueDate TEXT,
    itemId INTEGER,
    FOREIGN KEY (customerId) REFERENCES customer(customerId),
    FOREIGN KEY (itemId) REFERENCES item(itemId)
);
"""

ITEMS = [
    ("Book", "The Pragmatic Programmer", "David Thomas", 0),
    ("Book", "Clean Code", "Robert C. Martin", 0),
    ("Book", "Introduction to Algorithms", "Thomas H. Cormen", 1),
    ("Magazine", "National Geographic - March 2024", None, 0),
    ("CD", "Abbey Road", "The Beatles", 0),
    ("Record", "Kind of Blue", "Miles Davis", 0),
    ("Book", "Dune", "Frank Herbert", 0),
    ("Book", "The Hobbit", "J.R.R. Tolkien", 1),
    ("Online Book", "Structure and Interpretation of Computer Programs", "Harold Abelson", 0),
    ("Magazine", "Scientific American - January 2024", None, 0),
]

CUSTOMERS = [
    ("Alice Chen", "1998-04-12", "123 Maple St, Burnaby, BC", "alice.chen@example.com"),
    ("Ben Kaur", "2000-11-02", "456 Oak Ave, Vancouver, BC", "ben.kaur@example.com"),
    ("Carla Diaz", "1995-07-23", "789 Pine Rd, Surrey, BC", "carla.diaz@example.com"),
    ("Devon Wu", "2002-01-30", "22 Birch Ln, Coquitlam, BC", "devon.wu@example.com"),
    ("Priya Nair", "1999-09-15", "9 Cedar Ct, Richmond, BC", "priya.nair@example.com"),
]

ROOMS = [
    ("Meeting Room", 12),
    ("Study Hall", 40),
    ("Auditorium", 150),
]

EVENTS = [
    ("Intro to Python Workshop", "2026-10-05", 1, "Workshop"),
    ("Teen Book Club", "2026-10-12", 2, "Book Club"),
    ("Community Author Talk", "2026-10-20", 3, "Talk"),
]

EMPLOYEES = [
    ("Maria Santos", "Head Librarian", "2018-06-01", 68000),
    ("Jordan Lee", "Library Assistant", "2022-09-15", 42000),
]

PREVIOUS_EMPLOYEES = [
    ("Sam Okafor", "Library Assistant", "2015-03-01", "2021-08-30", 40000),
]

FUTURE_ITEMS = [
    ("Book", "2026-11-01", "Project Hail Mary", "Andy Weir"),
]

# One outstanding borrow, matching the two items marked isBorrowed = 1 above,
# so a fresh checkout of the repo has something to exercise "Return an item"
# and "Find an item" with right away.
BORROWS = [
    (1, "2026-10-05", 3),
    (1, "2026-10-10", 8),
]


def main():
    conn = sqlite3.connect(DB_PATH)
    try:
        with conn:
            cur = conn.cursor()
            cur.executescript(SCHEMA)

            cur.executemany(
                "INSERT INTO item (type, title, author, isBorrowed) VALUES (?, ?, ?, ?)",
                ITEMS,
            )
            cur.executemany(
                "INSERT INTO customer (name, birthDate, address, email) VALUES (?, ?, ?, ?)",
                CUSTOMERS,
            )
            cur.executemany("INSERT INTO room (type, capacity) VALUES (?, ?)", ROOMS)
            cur.executemany(
                "INSERT INTO event (name, date, roomId, type) VALUES (?, ?, ?, ?)",
                EVENTS,
            )
            cur.executemany(
                "INSERT INTO employee (name, position, startDate, salary) VALUES (?, ?, ?, ?)",
                EMPLOYEES,
            )
            cur.executemany(
                "INSERT INTO previousEmployee (name, position, startDate, endDate, salary) VALUES (?, ?, ?, ?, ?)",
                PREVIOUS_EMPLOYEES,
            )
            cur.executemany(
                "INSERT INTO futureItem (type, addDate, title, author) VALUES (?, ?, ?, ?)",
                FUTURE_ITEMS,
            )
            cur.executemany(
                "INSERT INTO borrow (customerId, dueDate, itemId) VALUES (?, ?, ?)",
                BORROWS,
            )
    finally:
        conn.close()

    print(f"Created and seeded {DB_PATH}")


if __name__ == "__main__":
    main()
