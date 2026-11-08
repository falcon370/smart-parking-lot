"""Unit tests for the Smart Parking Lot Management System.

Run from the project folder:  python -m unittest discover -s tests -v
Each test uses its own temporary database, so parking.db is never touched.
"""

import csv
import os
import shutil
import tempfile
import unittest
from datetime import datetime, timedelta

import database
from exceptions import (InvalidInputError, SlotStateError, SlotUnavailableError,
                        VehicleAlreadyParkedError, VehicleNotFoundError)
from parking_lot import ParkingLot
from parking_slot import ParkingSlot
from vehicle import Bike, Car, Vehicle, create_vehicle

T0 = datetime(2026, 1, 1, 9, 0, 0)


class FakeClock:
    """Stands in for datetime.now so tests can move time forward."""

    def __init__(self, start):
        self.now = start

    def __call__(self):
        return self.now

    def advance(self, **kwargs):
        self.now += timedelta(**kwargs)


class VehicleTests(unittest.TestCase):
    """Validation, abstraction and the create_vehicle factory."""

    def test_vehicle_is_abstract(self):
        with self.assertRaises(TypeError):
            Vehicle("KA01AB1234")

    def test_plate_is_normalised_to_upper_case(self):
        self.assertEqual(Car("  ka01ab1234 ").plate_number, "KA01AB1234")

    def test_invalid_plates_rejected(self):
        for plate in ["", "AB", "KA 01 AB", "THIS-IS-TOO-LONG", "AB@12"]:
            with self.subTest(plate=plate), self.assertRaises(InvalidInputError):
                Car(plate)

    def test_plate_setter_validates_updates(self):
        car = Car("KA01AB1234")
        with self.assertRaises(InvalidInputError):
            car.plate_number = "!!"
        self.assertEqual(car.plate_number, "KA01AB1234")  # unchanged

    def test_invalid_owner_rejected(self):
        with self.assertRaises(InvalidInputError):
            Car("KA01AB1234", "R2D2")
        with self.assertRaises(InvalidInputError):
            Car("KA01AB1234", "A" * 51)

    def test_factory_creates_right_subclass(self):
        self.assertIsInstance(create_vehicle("CAR", "KA01AB1234"), Car)
        self.assertIsInstance(create_vehicle("bike", "KA01AB1234"), Bike)
        with self.assertRaises(InvalidInputError):
            create_vehicle("truck", "KA01AB1234")


class FeeTests(unittest.TestCase):
    """Car and Bike fee rules (method overriding)."""

    def fee(self, vehicle, **duration):
        """Fee for a stay of the given length, e.g. fee(car, hours=2)."""
        return vehicle.calculate_fee(T0, T0 + timedelta(**duration))

    def test_minimum_one_hour(self):
        self.assertEqual(self.fee(Car("CAR1"), minutes=0), 20)
        self.assertEqual(self.fee(Bike("BIKE1"), minutes=5), 10)

    def test_started_hour_is_charged_in_full(self):
        self.assertEqual(self.fee(Car("CAR1"), hours=2, minutes=1), 60)

    def test_bike_daily_cap(self):
        self.assertEqual(self.fee(Bike("BIKE1"), hours=12), 100)        # capped
        self.assertEqual(self.fee(Bike("BIKE1"), hours=26), 100 + 20)   # 1 day + 2h

    def test_car_has_no_cap(self):
        self.assertEqual(self.fee(Car("CAR1"), hours=12), 240)

    def test_exit_before_entry_rejected(self):
        with self.assertRaises(InvalidInputError):
            Car("CAR1").calculate_fee(T0, T0 - timedelta(minutes=1))


class ParkingSlotTests(unittest.TestCase):
    """Slot state changes and read-only attributes."""

    def test_occupy_and_free(self):
        slot = ParkingSlot(1, "car")
        slot.occupy()
        self.assertTrue(slot.is_occupied)
        slot.free()
        self.assertFalse(slot.is_occupied)

    def test_cannot_occupy_twice_or_free_twice(self):
        slot = ParkingSlot(1, "car")
        with self.assertRaises(SlotStateError):
            slot.free()
        slot.occupy()
        with self.assertRaises(SlotStateError):
            slot.occupy()

    def test_occupied_flag_is_read_only(self):
        with self.assertRaises(AttributeError):
            ParkingSlot(1, "car").is_occupied = True

    def test_invalid_slot_rejected(self):
        with self.assertRaises(InvalidInputError):
            ParkingSlot(0, "car")
        with self.assertRaises(InvalidInputError):
            ParkingSlot(1, "truck")


class ParkingLotTests(unittest.TestCase):
    """End-to-end lot operations on a temporary database."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.old_db = database.DB_NAME
        database.DB_NAME = os.path.join(self.tmp, "test.db")
        self.clock = FakeClock(T0)
        self.lot = self.new_lot()

    def tearDown(self):
        database.DB_NAME = self.old_db
        shutil.rmtree(self.tmp)

    def new_lot(self):
        """Open a lot on the test database (2 car slots, 1 bike slot)."""
        return ParkingLot(car_slots=2, bike_slots=1,
                          receipts_dir=os.path.join(self.tmp, "receipts"),
                          clock=self.clock)

    def test_allocates_first_free_matching_slot(self):
        self.assertEqual(self.lot.park_vehicle(Car("CAR1")).slot_id, 1)
        self.assertEqual(self.lot.park_vehicle(Car("CAR2")).slot_id, 2)
        self.assertEqual(self.lot.park_vehicle(Bike("BIKE1")).slot_id, 3)

    def test_full_lot_raises(self):
        self.lot.park_vehicle(Bike("BIKE1"))
        with self.assertRaises(SlotUnavailableError):
            self.lot.park_vehicle(Bike("BIKE2"))

    def test_same_vehicle_cannot_park_twice(self):
        self.lot.park_vehicle(Car("CAR1"))
        with self.assertRaises(VehicleAlreadyParkedError):
            self.lot.park_vehicle(Car("CAR1"))

    def test_plate_type_mismatch_rejected(self):
        self.lot.park_vehicle(Car("SAME1"))
        self.clock.advance(hours=1)
        self.lot.remove_vehicle("SAME1")
        with self.assertRaises(InvalidInputError):
            self.lot.park_vehicle(Bike("SAME1"))

    def test_remove_charges_fee_frees_slot_and_saves_receipt(self):
        self.lot.park_vehicle(Car("CAR1"))
        self.clock.advance(hours=2, minutes=30)
        payment = self.lot.remove_vehicle("car1")  # lower case still matches
        self.assertEqual(payment.amount, 60)
        self.assertEqual(self.lot.availability()["car"], ([1, 2], 2))
        receipt = os.path.join(self.tmp, "receipts", f"receipt_{payment.payment_id}.txt")
        with open(receipt, encoding="utf-8") as f:
            self.assertIn("Rs. 60.00", f.read())

    def test_remove_unknown_vehicle_raises(self):
        with self.assertRaises(VehicleNotFoundError):
            self.lot.remove_vehicle("NOPE123")

    def test_vehicle_can_park_again_after_leaving(self):
        self.lot.park_vehicle(Car("CAR1"))
        self.lot.remove_vehicle("CAR1")
        self.assertEqual(self.lot.park_vehicle(Car("CAR1")).slot_id, 1)

    def test_state_survives_restart(self):
        self.lot.park_vehicle(Car("CAR1"))
        reopened = self.new_lot()
        self.assertEqual(reopened.availability()["car"], ([2], 2))
        self.assertEqual(reopened.active_vehicles()[0]["plate_number"], "CAR1")

    def test_history_and_csv_export(self):
        self.lot.park_vehicle(Car("CAR1"))
        self.lot.park_vehicle(Bike("BIKE1"))
        self.clock.advance(hours=1)
        self.lot.remove_vehicle("CAR1")
        self.lot.remove_vehicle("BIKE1")
        self.assertEqual([p.amount for p in self.lot.payment_history()], [20, 10])

        path, count = self.lot.export_payments_csv(os.path.join(self.tmp, "out.csv"))
        self.assertEqual(count, 2)
        with open(path, newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        self.assertEqual([r["plate_number"] for r in rows], ["CAR1", "BIKE1"])
        self.assertEqual(rows[0]["amount"], "20.00")


if __name__ == "__main__":
    unittest.main()
