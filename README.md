# Smart Parking Lot Management System

A menu-driven Python application that manages a parking lot. It allocates slots to cars and bikes, tracks which slots are free, calculates parking fees and generates receipts. Vehicles, parking slots and payments are stored in an SQLite database. Receipts are saved as text files, and payment history can be exported to CSV.

## Problem Statement

Manual parking management is slow and error-prone. Attendants have to find free slots by hand, note entry times on paper and work out fees themselves, which leads to lost records, wrong charges and disputes. A software system can allocate slots automatically, record every entry and exit, apply the correct tariff for each vehicle type and give the customer a receipt.

## Objectives

- Model a parking lot with object-oriented classes: `Vehicle`, `Car`, `Bike`, `ParkingSlot`, `ParkingLot` and `Payment`.
- Allocate the first free slot of the matching type (car or bike) when a vehicle arrives.
- Track slot availability in real time.
- Calculate parking fees using per-vehicle tariffs.
- Generate a receipt for every exit and keep a payment history.
- Store data in SQL (SQLite) so it is kept between runs, and use text and CSV files for receipts and reports.
- Validate all input and handle invalid operations with clear error messages.

## Project Description

The lot starts with **5 car slots (1–5)** and **5 bike slots (6–10)**. When a vehicle parks, the system:

1. checks that the plate number is valid and the vehicle is not already parked,
2. assigns the first free slot of the right type,
3. records the vehicle and its entry time in the database.

When the vehicle leaves, the system calculates the fee, marks the slot free, stores the payment and prints a receipt. The receipt is also saved to `receipts/receipt_<no>.txt`.

### Tariffs

| Vehicle | Rate | Rule |
|---|---|---|
| Car | Rs. 20 per hour | Every started hour is charged in full, with a minimum of 1 hour |
| Bike | Rs. 10 per hour | Same as car, but capped at Rs. 100 per day (24 hours) |

## How to Run

**Requirements:** Python 3.8 or newer. No extra packages are needed, since only the standard library is used (`sqlite3`, `csv`, `abc`, `datetime`).

```bash
git clone https://github.com/falcon370/smart-parking-lot.git
cd smart-parking-lot
python main.py
```

The database `parking.db` is created automatically on the first run. To start again with an empty lot, delete `parking.db`.

### Menu

```
========= SMART PARKING LOT =========
1. Park vehicle
2. Remove vehicle (pay and get receipt)
3. Show slot availability
4. Show parked vehicles
5. Show payment history
6. Export payments to CSV
7. Exit
=====================================
```

### Running the Tests

```bash
python -m unittest discover -s tests -v
```

The tests use a temporary database, so your real data is never changed. See [TEST_CASES.md](TEST_CASES.md) for the full list of test cases and their results.

## Project Structure

```
main.py           Menu-driven user interface
parking_lot.py    ParkingLot: allocation, fees, history, CSV export
vehicle.py        Vehicle (abstract), Car, Bike, create_vehicle() factory
parking_slot.py   ParkingSlot
payment.py        Payment: receipt text, receipt file, CSV row
database.py       SQLite connection and table creation
exceptions.py     Custom exception classes
tests/            Unit tests
docs/             Sample run output and screenshots
```

Files created while the program runs (not stored in git): `parking.db`, `receipts/`, `payments.csv`.

## UML Class Diagram

Each diagram fits on one screen, so it can be screenshotted directly from this page on GitHub.

**Legend:** `+` public · `-` private (read through a property) · *italic* = abstract · underlined = static or class method · `<|--` inheritance · `*--` composition (the lot owns its slots) · `..>` uses or creates

### Classes

```mermaid
classDiagram
    direction TB

    class Vehicle {
        <<abstract>>
        -plate_number : str
        -owner : str
        +vehicle_type()* str
        +hourly_rate()* int
        +calculate_fee(entry, exit)* int
        +billable_hours(entry, exit)$ int
    }
    class Car {
        +vehicle_type = "car"
        +hourly_rate = 20
        +calculate_fee(entry, exit) int
    }
    class Bike {
        +DAILY_CAP = 100
        +vehicle_type = "bike"
        +hourly_rate = 10
        +calculate_fee(entry, exit) int
    }
    class ParkingLot {
        +slots : list~ParkingSlot~
        +receipts_dir : str
        +park_vehicle(vehicle) ParkingSlot
        +remove_vehicle(plate) Payment
        +availability() dict
        +active_vehicles() list
        +payment_history() list~Payment~
        +export_payments_csv(path) tuple
    }
    class ParkingSlot {
        -slot_id : int
        -slot_type : str
        -is_occupied : bool
        +can_fit(vehicle) bool
        +occupy()
        +free()
    }
    class Payment {
        -payment_id : int
        -plate_number : str
        -vehicle_type : str
        -slot_id : int
        -entry_time : datetime
        -exit_time : datetime
        -amount : float
        +duration() str
        +receipt_text() str
        +save_receipt(folder) str
        +to_csv_row() list
        +from_row(row)$ Payment
    }

    Vehicle <|-- Car : inherits
    Vehicle <|-- Bike : inherits
    ParkingLot "1" *-- "many" ParkingSlot : owns
    ParkingLot ..> Vehicle : parks
    ParkingLot ..> Payment : creates
```

### Exception Hierarchy

```mermaid
classDiagram
    direction TB

    class Exception
    class ParkingError
    class InvalidInputError
    class SlotUnavailableError
    class SlotStateError
    class VehicleAlreadyParkedError
    class VehicleNotFoundError

    Exception <|-- ParkingError
    ParkingError <|-- InvalidInputError
    ParkingError <|-- SlotUnavailableError
    ParkingError <|-- SlotStateError
    ParkingError <|-- VehicleAlreadyParkedError
    ParkingError <|-- VehicleNotFoundError
```

### Database Schema

```mermaid
erDiagram
    vehicles ||--o{ payments : "has"
    parking_slots ||--o{ payments : "used in"
    vehicles {
        INTEGER vehicle_id PK
        TEXT plate_number UK
        TEXT vehicle_type
        TEXT owner
    }
    parking_slots {
        INTEGER slot_id PK
        TEXT slot_type
        INTEGER is_occupied
    }
    payments {
        INTEGER payment_id PK
        INTEGER vehicle_id FK
        INTEGER slot_id FK
        TEXT entry_time
        TEXT exit_time
        REAL amount
    }
```

A row is added to `payments` when a vehicle enters, with `exit_time` and `amount` empty. A vehicle counts as currently parked while its `exit_time` is empty, and the row is completed when it leaves.

## How the Requirements Are Met

| Requirement | Where it is implemented |
|---|---|
| Classes and objects (6 classes and an exception hierarchy) | `Vehicle`, `Car`, `Bike`, `ParkingSlot`, `ParkingLot`, `Payment` |
| **Abstraction** | `Vehicle` is an abstract base class (`ABC`). It cannot be created directly and declares the abstract members `vehicle_type`, `hourly_rate` and `calculate_fee`. |
| **Inheritance** | `Car` and `Bike` inherit from `Vehicle`, and all custom exceptions inherit from `ParkingError`. |
| **Method overriding** | `Car.calculate_fee` and `Bike.calculate_fee` each override the abstract method. Bike adds a daily cap. |
| **Polymorphism** | `ParkingLot.remove_vehicle` calls `vehicle.calculate_fee(...)` without knowing whether it is a car or a bike. `create_vehicle()` builds the right subclass from a type name. |
| **Encapsulation** | Private `__attributes` in `Vehicle`, `ParkingSlot` and `Payment`. Validating setters check plate numbers and owner names. `is_occupied` is read-only and only changes through `occupy()`/`free()`, which refuse invalid changes. |
| **Composition** | A `ParkingLot` owns its `ParkingSlot` objects and creates `Payment` objects. |
| **Exception handling** | Custom exceptions in `exceptions.py` (invalid plate or type, lot full, already parked, not found). The menu catches `ParkingError`, `sqlite3.Error`, `OSError` and `Ctrl+C`/`Ctrl+D`. |
| **Data between runs** | SQLite database (`parking.db`), text receipts (`receipts/*.txt`) and CSV export (`payments.csv`). |
| **Menu-driven interface** | `main.py` |

## Sample Input and Output

| Parking a car | Invalid input handled |
|---|---|
| <img src="docs/screenshots/02-car-parked.png" width="420" alt="Car parked in slot 1"> | <img src="docs/screenshots/03-error.png" width="420" alt="Error for unknown vehicle type"> |
| **Checkout and receipt** | **All 24 tests passing** |
| <img src="docs/screenshots/06-checkout.png" width="420" alt="Checkout receipt"> | <img src="docs/screenshots/09-test-results.png" width="420" alt="Unit test results"> |

More:
- [All 12 screenshots with explanations](docs/screenshots/README.md): menu, availability, parked vehicles, receipt file, CSV export, database schema and UML.
- [Full sample session as text](docs/sample_run.md), including multi-hour stays and the bike daily cap.
