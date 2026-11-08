"""Menu-driven interface for the Smart Parking Lot Management System."""

import sqlite3

from exceptions import ParkingError
from parking_lot import ParkingLot
from vehicle import VEHICLE_CLASSES, create_vehicle

MENU = """
========= SMART PARKING LOT =========
1. Park vehicle
2. Remove vehicle (pay and get receipt)
3. Show slot availability
4. Show parked vehicles
5. Show payment history
6. Export payments to CSV
7. Exit
====================================="""


def park(lot):
    vtype = input(f"Vehicle type ({'/'.join(VEHICLE_CLASSES)}): ")
    plate = input("Plate number: ")
    owner = input("Owner name (optional): ")
    vehicle = create_vehicle(vtype, plate, owner)
    slot = lot.park_vehicle(vehicle)
    print(f"{vehicle} parked in slot {slot.slot_id}.")


def remove(lot):
    payment = lot.remove_vehicle(input("Plate number: "))
    print()
    print(payment.receipt_text())
    print(f"Receipt saved to {lot.receipts_dir}")


def show_availability(lot):
    for slot_type, (free, total) in lot.availability().items():
        print(f"{slot_type.title():5} slots: {len(free)}/{total} free {free}")


def show_parked(lot):
    rows = lot.active_vehicles()
    if not rows:
        print("No vehicles are parked.")
        return
    print(f"{'Slot':<5}{'Plate':<14}{'Type':<6}{'Owner':<20}Entry time")
    for r in rows:
        print(f"{r['slot_id']:<5}{r['plate_number']:<14}{r['vehicle_type']:<6}"
              f"{(r['owner'] or '-'):<20}{r['entry_time'].replace('T', ' ')}")


def show_history(lot):
    payments = lot.payment_history()
    if not payments:
        print("No payments yet.")
        return
    print(f"{'No':<4}{'Plate':<14}{'Type':<6}{'Slot':<5}{'Duration':<10}Amount")
    for p in payments:
        print(f"{p.payment_id:<4}{p.plate_number:<14}{p.vehicle_type:<6}"
              f"{p.slot_id:<5}{p.duration:<10}Rs. {p.amount:.2f}")
    print(f"Total collected: Rs. {sum(p.amount for p in payments):.2f}")


def export_csv(lot):
    path, count = lot.export_payments_csv()
    print(f"Exported {count} payment(s) to {path}")


ACTIONS = {"1": park, "2": remove, "3": show_availability,
           "4": show_parked, "5": show_history, "6": export_csv}


def main():
    try:
        lot = ParkingLot(car_slots=5, bike_slots=5)
    except (sqlite3.Error, OSError) as e:
        print(f"Could not open the parking database: {e}")
        return

    while True:
        print(MENU)
        try:
            choice = input("Enter choice: ").strip()
            if choice == "7":
                print("Goodbye!")
                break
            action = ACTIONS.get(choice)
            if action is None:
                print("Invalid choice. Please enter a number from 1 to 7.")
                continue
            action(lot)
        except ParkingError as e:
            print(f"Error: {e}")
        except sqlite3.Error as e:
            print(f"Database error: {e}")
        except OSError as e:
            print(f"File error: {e}")
        except (KeyboardInterrupt, EOFError):
            print("\nExiting. Goodbye!")
            break


if __name__ == "__main__":
    main()
