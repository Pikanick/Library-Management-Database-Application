import sqlite3
conn = sqlite3.connect('library.db')
from datetime import datetime, timedelta
import random

def get_date_after_30_days():
    today = datetime.now()
    date_after_30_days = today + timedelta(days=30)
    return date_after_30_days.strftime("%Y-%m-%d")

def find_item():
    itemName = input("Input the item name you want to find: ")
    findItem = "SELECT * FROM item WHERE title = :itemName"

    cur.execute(findItem,{"itemName":itemName})

    rows=cur.fetchall()
    if rows:
        print("We do have the following item, " + itemName + ": ")
    else:
        print("Unfortunately, we do not have items named " + itemName + "!\n")

    print(rows)

    print("\n")    

def borrow_item():
    itemName = input("Input the item name you want to borrow: ")
    borrowItem = "SELECT * FROM item WHERE title = :itemName"

    cur.execute(borrowItem,{"itemName":itemName})
    items =cur.fetchall()
    if items:
        print("We do have the following item, " + itemName + ": ")
        print(items)
        borrow_id = input("Input the itemId you want to borrow: ")
        customerId = input("Input your customerId: ")
        selectedItem = "INSERT INTO borrow ( customerId, dueDate, itemId) VALUES(?,?,?)"

        try:
            cur.execute(selectedItem,(customerId,get_date_after_30_days(),borrow_id))
            print("Borrowed successful")
        except sqlite3.IntegrityError:
            print("ERROR: There was a problem borrow the item!\n")

def return_item():
    customerId = input("Input your customer id: ")
    borrowedItem = "SELECT * FROM borrow WHERE customerId = :customerId"
    cur.execute(borrowedItem,{"customerId": customerId})
    items = cur.fetchall()
    if items:
        print("You have borrowed following item, which one you would like to return: ")
        print(items)
        selectedItem = input("Input the borrowId you would like to return: ")
        returnItem = "DELETE FROM borrow WHERE borrowId = :borrowId"
        try:
            cur.execute(returnItem,{"borrowId":selectedItem})
            print("Return successful")
        except sqlite3.IntegrityError:
            print("ERROR: There was a problem return the item!\n")

def donate_item():
    bookTitle = input("Thanks for donating, could you input the book title of your donation: ")
    type = input("Could you please input the book type: ")
    author = input("Could you please input the author name: ")
    donateItem = "INSERT INTO item ( type, title, author) VALUES(?,?,?)"
    try:
        cur.execute(donateItem,(type,bookTitle,author))
        print("Thanks for your donating")
    except sqlite3.IntegrityError:
        print("ERROR: There was a problem donate the item!\n")

def find_event():
    name = input("Please input the event name you want to find: ")
    findEvent = "SELECT * FROM event WHERE name = :eventName"
    cur.execute(findEvent,{"eventName":name})

    rows=cur.fetchall()
    if rows:
        print("We do have the following event: ")
    else:
        print("Unfortunately, we do not have events named " + name + "!\n")

    print(rows)

    print("\n")    

def register_event():
    eventId = input("Please input the event Id you want to register: ")
    findEvent = "SELECT * FROM event WHERE eventId = :eventId"
    cur.execute(findEvent,{"eventId":eventId})

    rows=cur.fetchall()
    if rows:
        customerId = input("Please input your customer ID: ")
        attendEvent = "INSERT INTO eventAttend (eventId,customerId) VALUES (?, ?)"
        try:
            cur.execute(attendEvent,(eventId,customerId))
            print("Register successfull")
        except sqlite3.IntegrityError:
            print("ERROR: There was a problem registering event!\n")
    else:
        print("Unfortunately, we do not have events you are looking for.")

def volunteer():
    name = input("Please input your name: ")
    position = "Volunteer"
    startDate = datetime.now().strftime("%Y-%m-%d")
    salary = 0
    registerVolunteer = "INSERT INTO employee (name, position, startDate, salary) VALUES (?, ?, ?, ?)"
    try:
        cur.execute(registerVolunteer,(name,position,startDate,salary))
        print("Register successfull, thanks for being volunteer")
    except sqlite3.IntegrityError:
        print("ERROR: There was a problem! You can not be an volunteer!\n")

def askForHelp():
    help = input("Please input your issue: ")
    print("Got it, a librarian will soon contact with you!")

instruction = input("1.Find an item in the library \n"
                 "2.Borrow an item from the library \n"
                 "3.Return a borrowed item \n"
                 "4.Donate an item to the library \n"
                 "5.Find an event in the library \n"
                 "6.Register for an event in the library \n"
                 "7.Volunteer for the library \n"
                 "8.Ask for help from a librarian \n"
                 "Enter the instruction number you want to execute: ")

cursor = conn.cursor()
print("Opened database successfully \n")

with conn:

    cur = conn.cursor()
    if(instruction == '1'):
        find_item()
        
    elif(instruction == '2'):
        borrow_item()

    elif(instruction == '3'):
        return_item()

    elif(instruction == '4'):
        donate_item()

    elif(instruction == '5'):
        find_event()

    elif(instruction == '6'):
        register_event()

    elif(instruction == '7'):
        volunteer()

    elif(instruction == '8'):
        askForHelp()

    else:
        print("Please input a valid code")
    
if conn:
    conn.close()
    print("Closed database successfully")

