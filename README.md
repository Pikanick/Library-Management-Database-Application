# Library-Management-Database-Application
This project is a comprehensive Library Management Database Application developed using Python and SQLite. The application allows library staff to manage items, customers, borrowings, fines, events, and employee records efficiently.
## Features
- **Item Management**: Manage library items including print books, online books, magazines, CDs, records, etc.
- **Customer Management**: Maintain detailed records of library members.
- **Borrow and Return** Management: Track items borrowed and returned by members, along with due dates.
- **Fine Management**: Manage fines for overdue items.
- **Event Management**: Organize and track library events and attendees.
- **Employee Management**: Keep records of current and past library employees.
- **Future Acquisitions**: Maintain records of items to be added to the library in the future.
## Database Design
**Entities and Relationships**
- Item: Stores information about all items in the library.
  - `itemId (Primary Key)`, `type`, `title`, `author`, `isBorrowed`
- Customer: Stores information about library members.
  - `customerId (Primary Key)`, `name`, `birthDate`, `address`, `email`
- Borrow: Manages borrowed items.
  - `borrowId (Primary Key)`, `customerId (Foreign Key)`, `itemId (Foreign Key)`, `dueDate`
- Fine: Manages fines for overdue items.
  - `fineId (Primary Key)`, `customerId (Foreign Key)`, `amount`
- Event: Manages library events.
  - `eventId (Primary Key)`, `name`, `date`, `roomId (Foreign Key)`, `type`
- Room: Stores information about library rooms.
  - `roomId (Primary Key)`, `type`, `capacity`
- RecommendAudience: Associates specific audiences with events.
  - `eventId (Primary Key, Foreign Key)`, `customerId (Primary Key, Foreign Key)`
- EventAttend: Tracks attendance of events by members.
  - `eventId (Primary Key, Foreign Key)`, `customerId (Primary Key, Foreign Key)`
- Employee: Stores information about library employees.
  - `employeeId (Primary Key)`, `name`, `position`, `startDate`, `salary`
- PreviousEmployee: Stores information about past employees.
  - `previousEmployeeId (Primary Key)`, `name`, `position`, `startDate`, `endDate`, `salary`
- FutureItem: Keeps records of potential future library items.
  - `futureItemId (Primary Key)`, `type`, `addDate`, `title`, `author`

## Functional Dependencies and BCNF
All tables are in BCNF as each non-trivial functional dependency has a superkey as the determinant, ensuring the database design avoids anomalies.

## Installation
- Clone the repository:
```python
  git clone https://github.com/yourusername/library-management.git
  cd library-management
```
- Install required packages:
```
  pip install -r requirements.txt
```
- Set up the database:
```
  python setup_database.py
```
## Usage
- Run the application:
```
  python library_app.py
```
- Features:
  - Find an item
  - Borrow an item
  - Return an item
  - Donate an item
  - Find an event
  - Register for an event
  - Volunteer for the library
  - Ask for help from a librarian

## License
This project is licensed under the MIT License.
