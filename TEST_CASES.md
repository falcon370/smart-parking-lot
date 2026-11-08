# Test Cases and Results

Automated tests are in [tests/test_parking.py](tests/test_parking.py). Run them with:

```bash
python -m unittest discover -s tests -v
```

**Result: 24 tests run, 24 passed** (Python 3.13, Windows 11).

## Vehicle (encapsulation, abstraction)

| ID | Test | Input | Expected result | Result |
|---|---|---|---|---|
| V1 | Abstract class cannot be created | `Vehicle("KA01AB1234")` | `TypeError` | Pass |
| V2 | Plate number normalised | `Car("  ka01ab1234 ")` | Plate is `KA01AB1234` | Pass |
| V3 | Invalid plates rejected | `""`, `"AB"`, `"KA 01 AB"`, `"THIS-IS-TOO-LONG"`, `"AB@12"` | `InvalidInputError` for each | Pass |
| V4 | Setter validates updates | `car.plate_number = "!!"` | `InvalidInputError`, old plate kept | Pass |
| V5 | Invalid owner rejected | `"R2D2"`, a 51-character name | `InvalidInputError` | Pass |
| V6 | Factory creates the right subclass | `"CAR"`, `"bike"`, `"truck"` | `Car`, `Bike`, `InvalidInputError` | Pass |

## Fee calculation (method overriding, polymorphism)

| ID | Test | Input | Expected result | Result |
|---|---|---|---|---|
| F1 | Minimum one hour | Car 0 min, Bike 5 min | Rs. 20, Rs. 10 | Pass |
| F2 | Started hour charged in full | Car 2h 1m | Rs. 60 (3 hours) | Pass |
| F3 | Bike daily cap | Bike 12h; Bike 26h | Rs. 100; Rs. 120 (1 day + 2h) | Pass |
| F4 | Car has no cap | Car 12h | Rs. 240 | Pass |
| F5 | Exit before entry | Exit 1 minute before entry | `InvalidInputError` | Pass |

## Parking slot

| ID | Test | Input | Expected result | Result |
|---|---|---|---|---|
| S1 | Occupy and free | `occupy()` then `free()` | `is_occupied` True, then False | Pass |
| S2 | Invalid state changes | `free()` on a free slot, `occupy()` twice | `SlotStateError` | Pass |
| S3 | Occupied flag is read-only | `slot.is_occupied = True` | `AttributeError` | Pass |
| S4 | Invalid slot rejected | id `0`, type `"truck"` | `InvalidInputError` | Pass |

## Parking lot (composition, SQL storage, file handling)

Each test uses a fresh temporary database with 2 car slots and 1 bike slot.

| ID | Test | Input | Expected result | Result |
|---|---|---|---|---|
| L1 | Allocate first free matching slot | Park CAR1, CAR2, BIKE1 | Slots 1, 2, 3 | Pass |
| L2 | Lot full | Park a second bike | `SlotUnavailableError` | Pass |
| L3 | Duplicate parking | Park CAR1 twice | `VehicleAlreadyParkedError` | Pass |
| L4 | Plate registered as another type | SAME1 parked as car, later as bike | `InvalidInputError` | Pass |
| L5 | Remove: fee, free slot, receipt file | Park CAR1, 2h 30m, remove `"car1"` | Rs. 60, slot 1 free, receipt file has `Rs. 60.00` | Pass |
| L6 | Remove unknown vehicle | Remove `NOPE123` | `VehicleNotFoundError` | Pass |
| L7 | Park again after leaving | Park, remove, park CAR1 | Slot 1 again | Pass |
| L8 | Data kept between runs | Park CAR1, create a new `ParkingLot` | Slot 1 still occupied, CAR1 listed | Pass |
| L9 | Payment history and CSV export | Park and remove CAR1 and BIKE1 after 1h | History Rs. 20, Rs. 10; CSV has 2 rows | Pass |

## Manual menu tests

These were run through `python main.py`. The output is in [docs/sample_run.md](docs/sample_run.md).

| ID | Test | Input | Expected result | Result |
|---|---|---|---|---|
| M1 | Invalid menu choice | `9` | "Invalid choice" message, menu shown again | Pass |
| M2 | Unknown vehicle type | `truck` | Error message, program continues | Pass |
| M3 | Invalid plate | `!!` | Error message, program continues | Pass |
| M4 | Remove a vehicle that isn't parked | `NOPE123` | Error message, program continues | Pass |
| M5 | End of input | Ctrl+Z then Enter (Windows) / Ctrl+D (Linux, macOS) at a prompt | "Exiting. Goodbye!", no traceback | Pass |
| M6 | Data kept after restart | Park a bike, exit, run again, choose 4 | Bike still listed as parked | Pass |
