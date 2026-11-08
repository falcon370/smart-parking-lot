"""The parking lot: allocates slots, charges fees and keeps records.

OOP concepts shown here:
    Composition   A ParkingLot owns a list of ParkingSlot objects and creates
                  Payment objects; they exist as parts of the lot.
    Polymorphism  remove_vehicle() calls vehicle.calculate_fee() without
                  knowing whether the vehicle is a Car or a Bike.

Design notes:
    - The SQLite database is the source of truth; ``self.slots`` is an
      in-memory copy of the parking_slots table. Every change updates both
      inside one database transaction.
    - Methods never print. They return results or raise ParkingError
      subclasses, and main.py decides what to show the user.
"""

import csv
import os
from datetime import datetime

import database
from exceptions import (InvalidInputError, SlotUnavailableError,
                        VehicleAlreadyParkedError, VehicleNotFoundError)
from parking_slot import SLOT_TYPES, ParkingSlot
from payment import CSV_HEADER, Payment
from vehicle import create_vehicle

# Project folder; default location for receipts/ and payments.csv.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class ParkingLot:
    """Manages all parking slots and parking sessions.

    Attributes:
        slots (list[ParkingSlot]): Every slot in the lot, ordered by id.
        receipts_dir (str): Folder where receipt text files are saved.
    """

    def __init__(self, car_slots=5, bike_slots=5, receipts_dir=None, clock=datetime.now):
        """Open the lot, creating the database and slots on the first run.

        Args:
            car_slots: Number of car slots, used only for a new database.
            bike_slots: Number of bike slots, used only for a new database.
            receipts_dir: Where to save receipts (default: <project>/receipts).
            clock: Function returning the current time. Tests pass a fake
                clock to simulate time passing.

        Raises:
            InvalidInputError: If a slot count is negative.
        """
        if car_slots < 0 or bike_slots < 0:
            raise InvalidInputError("Slot counts cannot be negative.")
        self.receipts_dir = receipts_dir or os.path.join(BASE_DIR, "receipts")
        self._clock = clock
        self.slots = []
        database.init_db()
        self._load_slots(car_slots, bike_slots)

    def _load_slots(self, car_slots, bike_slots):
        """Create slots in an empty database, then load them into self.slots.

        Car slots are numbered first (1..car_slots), then bike slots.
        If the database already has slots, the counts are ignored.
        """
        with database.get_connection() as conn:
            if conn.execute("SELECT COUNT(*) FROM parking_slots").fetchone()[0] == 0:
                types = ["car"] * car_slots + ["bike"] * bike_slots
                conn.executemany(
                    "INSERT INTO parking_slots (slot_id, slot_type) VALUES (?, ?)",
                    list(enumerate(types, start=1)),
                )
            for r in conn.execute("SELECT * FROM parking_slots ORDER BY slot_id"):
                self.slots.append(
                    ParkingSlot(r["slot_id"], r["slot_type"], bool(r["is_occupied"]))
                )

    def _find_slot(self, slot_id):
        """Return the in-memory ParkingSlot with the given id."""
        return next(s for s in self.slots if s.slot_id == slot_id)

    # ------------------------------------------------------------------
    # Parking operations
    # ------------------------------------------------------------------
    def park_vehicle(self, vehicle):
        """Park a vehicle in the first free slot of its type.

        Records the vehicle (if new) and its entry time, and marks the slot
        occupied.

        Args:
            vehicle (Vehicle): The Car or Bike arriving.

        Returns:
            ParkingSlot: The slot that was allocated.

        Raises:
            InvalidInputError: If the plate is already registered as a
                different vehicle type.
            VehicleAlreadyParkedError: If the vehicle is already parked.
            SlotUnavailableError: If no matching slot is free.
        """
        now = self._clock().replace(microsecond=0)
        with database.get_connection() as conn:
            # 1. Validate against what is already stored for this plate.
            existing = conn.execute(
                "SELECT vehicle_id, vehicle_type FROM vehicles WHERE plate_number = ?",
                (vehicle.plate_number,),
            ).fetchone()
            if existing and existing["vehicle_type"] != vehicle.vehicle_type:
                raise InvalidInputError(
                    f"{vehicle.plate_number} is registered as a {existing['vehicle_type']}."
                )
            if existing and conn.execute(
                "SELECT 1 FROM payments WHERE vehicle_id = ? AND exit_time IS NULL",
                (existing["vehicle_id"],),
            ).fetchone():
                raise VehicleAlreadyParkedError(f"{vehicle.plate_number} is already parked.")

            # 2. Find a free slot of the right type.
            slot = next((s for s in self.slots if s.can_fit(vehicle)), None)
            if slot is None:
                raise SlotUnavailableError(f"No free {vehicle.vehicle_type} slot available.")

            # 3. Save the vehicle (new or returning) and open a parking session.
            if existing:
                vehicle_id = existing["vehicle_id"]
                if vehicle.owner:
                    conn.execute("UPDATE vehicles SET owner = ? WHERE vehicle_id = ?",
                                 (vehicle.owner, vehicle_id))
            else:
                vehicle_id = conn.execute(
                    "INSERT INTO vehicles (plate_number, vehicle_type, owner) VALUES (?, ?, ?)",
                    (vehicle.plate_number, vehicle.vehicle_type, vehicle.owner),
                ).lastrowid
            conn.execute(
                "INSERT INTO payments (vehicle_id, slot_id, entry_time) VALUES (?, ?, ?)",
                (vehicle_id, slot.slot_id, now.isoformat()),
            )

            # 4. Mark the slot occupied in the database and in memory.
            conn.execute("UPDATE parking_slots SET is_occupied = 1 WHERE slot_id = ?",
                         (slot.slot_id,))
            slot.occupy()
        return slot

    def remove_vehicle(self, plate_number):
        """Check a vehicle out: charge the fee, free its slot, save a receipt.

        Args:
            plate_number (str): Plate of the leaving vehicle (any case).

        Returns:
            Payment: The completed payment, with its receipt saved to
            ``receipts_dir``.

        Raises:
            VehicleNotFoundError: If the vehicle is not currently parked.
            OSError: If the receipt file cannot be written.
        """
        plate = str(plate_number).strip().upper()
        exit_time = self._clock().replace(microsecond=0)
        with database.get_connection() as conn:
            # Find the open parking session for this plate.
            row = conn.execute(
                "SELECT p.payment_id, p.slot_id, p.entry_time, v.vehicle_type, v.owner "
                "FROM payments p JOIN vehicles v ON v.vehicle_id = p.vehicle_id "
                "WHERE v.plate_number = ? AND p.exit_time IS NULL",
                (plate,),
            ).fetchone()
            if row is None:
                raise VehicleNotFoundError(f"No active parking record for {plate}.")

            # Rebuild the right Vehicle subclass so its own tariff is applied.
            vehicle = create_vehicle(row["vehicle_type"], plate, row["owner"] or "")
            entry_time = datetime.fromisoformat(row["entry_time"])
            fee = vehicle.calculate_fee(entry_time, exit_time)  # polymorphic call

            # Close the session and free the slot.
            conn.execute(
                "UPDATE payments SET exit_time = ?, amount = ? WHERE payment_id = ?",
                (exit_time.isoformat(), fee, row["payment_id"]),
            )
            conn.execute("UPDATE parking_slots SET is_occupied = 0 WHERE slot_id = ?",
                         (row["slot_id"],))
            self._find_slot(row["slot_id"]).free()

        payment = Payment(row["payment_id"], plate, vehicle.vehicle_type,
                          row["slot_id"], entry_time, exit_time, fee)
        payment.save_receipt(self.receipts_dir)
        return payment

    # ------------------------------------------------------------------
    # Reports
    # ------------------------------------------------------------------
    def availability(self):
        """Return free slots per type.

        Returns:
            dict: ``{slot_type: (free_slot_ids, total_slots)}``, e.g.
            ``{"car": ([2, 3], 5), "bike": ([6, 7, 8, 9, 10], 5)}``.
        """
        result = {}
        for t in SLOT_TYPES:
            of_type = [s for s in self.slots if s.slot_type == t]
            result[t] = ([s.slot_id for s in of_type if not s.is_occupied], len(of_type))
        return result

    def active_vehicles(self):
        """Return database rows for every vehicle currently parked.

        Each row has plate_number, vehicle_type, owner, slot_id, entry_time.
        """
        with database.get_connection() as conn:
            return conn.execute(
                "SELECT v.plate_number, v.vehicle_type, v.owner, p.slot_id, p.entry_time "
                "FROM payments p JOIN vehicles v ON v.vehicle_id = p.vehicle_id "
                "WHERE p.exit_time IS NULL ORDER BY p.slot_id"
            ).fetchall()

    def payment_history(self):
        """Return every completed payment as a list of Payment, oldest first."""
        with database.get_connection() as conn:
            rows = conn.execute(
                "SELECT p.payment_id, v.plate_number, v.vehicle_type, p.slot_id, "
                "p.entry_time, p.exit_time, p.amount "
                "FROM payments p JOIN vehicles v ON v.vehicle_id = p.vehicle_id "
                "WHERE p.exit_time IS NOT NULL ORDER BY p.payment_id"
            ).fetchall()
        return [Payment.from_row(r) for r in rows]

    def export_payments_csv(self, path=None):
        """Write the payment history to a CSV file (overwrites the file).

        Args:
            path: Output file (default: <project>/payments.csv).

        Returns:
            tuple: ``(path, number_of_rows_written)``.

        Raises:
            OSError: If the file cannot be written (e.g. open in Excel).
        """
        path = path or os.path.join(BASE_DIR, "payments.csv")
        payments = self.payment_history()
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(CSV_HEADER)
            writer.writerows(p.to_csv_row() for p in payments)
        return path, len(payments)
