from datetime import datetime

from database import get_connection
from parking_slot import ParkingSlot
from vehicle import VEHICLE_CLASSES


class ParkingLot:
    def __init__(self, car_slots=5, bike_slots=5):
        self.slots = []  # Composition: a lot HAS slots
        self._load_slots(car_slots, bike_slots)

    def _load_slots(self, car_slots, bike_slots):
        with get_connection() as conn:
            if conn.execute("SELECT COUNT(*) FROM parking_slots").fetchone()[0] == 0:
                types = ["car"] * car_slots + ["bike"] * bike_slots
                for i, t in enumerate(types, start=1):
                    conn.execute(
                        "INSERT INTO parking_slots (slot_id, slot_type) VALUES (?, ?)",
                        (i, t),
                    )
            for r in conn.execute("SELECT * FROM parking_slots ORDER BY slot_id"):
                self.slots.append(
                    ParkingSlot(r["slot_id"], r["slot_type"], bool(r["is_occupied"]))
                )

    def park_vehicle(self, vehicle):
        slot = next(
            (s for s in self.slots
             if not s.is_occupied and s.slot_type == vehicle.vehicle_type),
            None,
        )
        if slot is None:
            print(f"No free {vehicle.vehicle_type} slot available.")
            return
        now = datetime.now().isoformat(timespec="seconds")
        with get_connection() as conn:
            conn.execute(
                "INSERT OR IGNORE INTO vehicles (plate_number, vehicle_type, owner) "
                "VALUES (?, ?, ?)",
                (vehicle.plate_number, vehicle.vehicle_type, vehicle.owner),
            )
            vid = conn.execute(
                "SELECT vehicle_id FROM vehicles WHERE plate_number = ?",
                (vehicle.plate_number,),
            ).fetchone()[0]
            conn.execute(
                "INSERT INTO payments (vehicle_id, slot_id, entry_time) VALUES (?, ?, ?)",
                (vid, slot.slot_id, now),
            )
            conn.execute(
                "UPDATE parking_slots SET is_occupied = 1 WHERE slot_id = ?",
                (slot.slot_id,),
            )
        slot.occupy()
        print(f"Vehicle {vehicle.plate_number} parked in slot {slot.slot_id}.")

    def remove_vehicle(self, plate_number):
        with get_connection() as conn:
            row = conn.execute(
                "SELECT p.payment_id, p.slot_id, p.entry_time, v.vehicle_type, v.owner "
                "FROM payments p JOIN vehicles v ON v.vehicle_id = p.vehicle_id "
                "WHERE v.plate_number = ? AND p.exit_time IS NULL",
                (plate_number,),
            ).fetchone()
            if row is None:
                print("No active parking record for that vehicle.")
                return
            vehicle = VEHICLE_CLASSES[row["vehicle_type"]](plate_number, row["owner"])
            entry = datetime.fromisoformat(row["entry_time"])
            exit_ = datetime.now()
            fee = vehicle.calculate_fee(entry, exit_)  # polymorphic call
            conn.execute(
                "UPDATE payments SET exit_time = ?, amount = ? WHERE payment_id = ?",
                (exit_.isoformat(timespec="seconds"), fee, row["payment_id"]),
            )
            conn.execute(
                "UPDATE parking_slots SET is_occupied = 0 WHERE slot_id = ?",
                (row["slot_id"],),
            )
        for s in self.slots:
            if s.slot_id == row["slot_id"]:
                s.free()
        self.print_receipt(plate_number, row["slot_id"], entry, exit_, fee)

    def show_availability(self):
        for t in ("car", "bike"):
            free = [s.slot_id for s in self.slots if s.slot_type == t and not s.is_occupied]
            total = sum(1 for s in self.slots if s.slot_type == t)
            print(f"{t.title()} slots: {len(free)}/{total} free {free}")

    @staticmethod
    def print_receipt(plate, slot_id, entry, exit_, fee):
        print("\n------- PARKING RECEIPT -------")
        print(f"Vehicle : {plate}")
        print(f"Slot    : {slot_id}")
        print(f"Entry   : {entry}")
        print(f"Exit    : {exit_:%Y-%m-%d %H:%M:%S}")
        print(f"Amount  : Rs. {fee}")
        print("-------------------------------\n")
