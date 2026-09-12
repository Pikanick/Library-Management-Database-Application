import sqlite3
from datetime import datetime, timedelta


def get_date_after_30_days():
    today = datetime.now()
    date_after_30_days = today + timedelta(days=30)
    return date_after_30_days.strftime("%Y-%m-%d")


def prompt_int(prompt):
    """Keep asking until the user enters a valid whole number, or an empty
    line to cancel (returns None). Every place that used to do
    `input(...)` for an id (customerId, itemId, borrowId, eventId) used to
    hand whatever the user typed straight to a query with no validation,
    so a typo just silently matched zero rows instead of telling the user
    what went wrong."""
    while True:
        value = input(prompt).strip()
        if value == "":
            return None
        if value.lstrip("-").isdigit():
            return int(value)
        print("Please enter a whole number (or leave blank to cancel).")


def find_item(cur):
    itemName = input("Input the item name you want to find: ")
    cur.execute("SELECT * FROM item WHERE title = :itemName", {"itemName": itemName})

    rows = cur.fetchall()
    if rows:
        print("We do have the following item, " + itemName + ": ")
        print(rows)
    else:
        print("Unfortunately, we do not have items named " + itemName + "!\n")
    print()


def borrow_item(cur):
    itemName = input("Input the item name you want to borrow: ")
    # Only offer items that aren't already checked out. The original
    # query didn't filter on isBorrowed at all, so it would happily let
    # someone "borrow" a copy that was already out, and never touched
    # isBorrowed either way -- the column existed in the schema but the
    # app never read or wrote it.
    cur.execute(
        "SELECT * FROM item WHERE title = :itemName AND isBorrowed = 0",
        {"itemName": itemName},
    )
    items = cur.fetchall()
    if not items:
        print("Sorry, there's no available (not already borrowed) item named " + itemName + ".\n")
        return

    print("We do have the following available item(s), " + itemName + ": ")
    print(items)
    available_ids = {row[0] for row in items}

    borrow_id = prompt_int("Input the itemId you want to borrow: ")
    if borrow_id is None:
        return
    if borrow_id not in available_ids:
        print("That itemId isn't one of the available items shown above.\n")
        return

    customerId = prompt_int("Input your customerId: ")
    if customerId is None:
        return

    try:
        cur.execute(
            "INSERT INTO borrow (customerId, dueDate, itemId) VALUES(?,?,?)",
            (customerId, get_date_after_30_days(), borrow_id),
        )
        cur.execute("UPDATE item SET isBorrowed = 1 WHERE itemId = ?", (borrow_id,))
        print("Borrowed successful")
    except sqlite3.IntegrityError:
        print("ERROR: There was a problem borrowing the item!\n")


def return_item(cur):
    customerId = prompt_int("Input your customer id: ")
    if customerId is None:
        return
    cur.execute("SELECT * FROM borrow WHERE customerId = :customerId", {"customerId": customerId})
    items = cur.fetchall()
    if not items:
        print("You don't have any borrowed items on file.\n")
        return

    print("You have borrowed the following item(s), which one would you like to return: ")
    print(items)
    own_borrow_ids = {row[0] for row in items}
    borrow_id_to_item = {row[0]: row[3] for row in items}  # borrowId -> itemId

    selected = prompt_int("Input the borrowId you would like to return: ")
    if selected is None:
        return
    # The original deleted whatever borrowId was typed, with no check that
    # it was actually one of *this* customer's borrows.
    if selected not in own_borrow_ids:
        print("That borrowId isn't one of your borrowed items.\n")
        return

    try:
        cur.execute("DELETE FROM borrow WHERE borrowId = ?", (selected,))
        cur.execute("UPDATE item SET isBorrowed = 0 WHERE itemId = ?", (borrow_id_to_item[selected],))
        print("Return successful")
    except sqlite3.IntegrityError:
        print("ERROR: There was a problem returning the item!\n")


def donate_item(cur):
    bookTitle = input("Thanks for donating, could you input the book title of your donation: ")
    itemType = input("Could you please input the book type: ")
    author = input("Could you please input the author name: ")
    try:
        cur.execute(
            "INSERT INTO item (type, title, author) VALUES(?,?,?)",
            (itemType, bookTitle, author),
        )
        print("Thanks for your donation")
    except sqlite3.IntegrityError:
        print("ERROR: There was a problem donating the item!\n")


def find_event(cur):
    name = input("Please input the event name you want to find: ")
    cur.execute("SELECT * FROM event WHERE name = :eventName", {"eventName": name})

    rows = cur.fetchall()
    if rows:
        print("We do have the following event: ")
        print(rows)
    else:
        print("Unfortunately, we do not have events named " + name + "!\n")
    print()


def register_event(cur):
    eventId = prompt_int("Please input the event Id you want to register: ")
    if eventId is None:
        return
    cur.execute("SELECT * FROM event WHERE eventId = :eventId", {"eventId": eventId})

    rows = cur.fetchall()
    if not rows:
        print("Unfortunately, we do not have the event you are looking for.")
        return

    customerId = prompt_int("Please input your customer ID: ")
    if customerId is None:
        return
    try:
        cur.execute(
            "INSERT INTO eventAttend (eventId, customerId) VALUES (?, ?)",
            (eventId, customerId),
        )
        print("Register successful")
    except sqlite3.IntegrityError:
        print("ERROR: There was a problem registering for the event!\n")


def volunteer(cur):
    name = input("Please input your name: ")
    position = "Volunteer"
    startDate = datetime.now().strftime("%Y-%m-%d")
    salary = 0
    try:
        cur.execute(
            "INSERT INTO employee (name, position, startDate, salary) VALUES (?, ?, ?, ?)",
            (name, position, startDate, salary),
        )
        print("Register successful, thanks for being a volunteer")
    except sqlite3.IntegrityError:
        print("ERROR: There was a problem registering you as a volunteer!\n")


def ask_for_help():
    input("Please input your issue: ")
    print("Got it, a librarian will contact you soon!")


MENU = (
    "1. Find an item in the library\n"
    "2. Borrow an item from the library\n"
    "3. Return a borrowed item\n"
    "4. Donate an item to the library\n"
    "5. Find an event in the library\n"
    "6. Register for an event in the library\n"
    "7. Volunteer for the library\n"
    "8. Ask for help from a librarian\n"
    "0. Exit\n"
    "Enter the instruction number you want to execute: "
)

ACTIONS = {
    "1": find_item,
    "2": borrow_item,
    "3": return_item,
    "4": donate_item,
    "5": find_event,
    "6": register_event,
    "7": volunteer,
}


def run_one_instruction(cur, instruction):
    """Dispatch a single menu choice. Returns False for '0' (exit),
    True otherwise (including on an unrecognized choice)."""
    if instruction == "0":
        return False
    if instruction == "8":
        ask_for_help()
    elif instruction in ACTIONS:
        ACTIONS[instruction](cur)
    else:
        print("Please input a valid code")
    return True


def main():
    conn = sqlite3.connect("library.db")
    print("Opened database successfully\n")
    try:
        with conn:
            cur = conn.cursor()
            # The original script only ever handled one instruction and
            # exited; the menu is naturally a repeat-until-quit loop.
            while True:
                instruction = input(MENU)
                if not run_one_instruction(cur, instruction):
                    break
                conn.commit()
    finally:
        conn.close()
        print("Closed database successfully")


if __name__ == "__main__":
    main()
