from database import init_db
from parking_lot import ParkingLot
from vehicle import VEHICLE_CLASSES


def main():
    init_db()
    lot = ParkingLot(car_slots=5, bike_slots=5)
    while True:
        print("1. Park vehicle  2. Remove vehicle  3. Availability  4. Exit")
        choice = input("Choice: ").strip()
        if choice == "1":
            vtype = input("Type (car/bike): ").strip().lower()
            if vtype not in VEHICLE_CLASSES:
                print("Invalid type.")
                continue
            plate = input("Plate number: ").strip().upper()
            owner = input("Owner name: ").strip()
            lot.park_vehicle(VEHICLE_CLASSES[vtype](plate, owner))
        elif choice == "2":
            lot.remove_vehicle(input("Plate number: ").strip().upper())
        elif choice == "3":
            lot.show_availability()
        elif choice == "4":
            break
        else:
            print("Invalid choice.")


if __name__ == "__main__":
    main()
