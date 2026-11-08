"""A completed parking payment and its receipt."""

import os
from datetime import datetime

TIME_FORMAT = "%Y-%m-%d %H:%M:%S"
CSV_HEADER = ["payment_id", "plate_number", "vehicle_type", "slot_id",
              "entry_time", "exit_time", "amount"]


class Payment:
    """One parking session that has been paid for.

    It knows how to format itself as a receipt, save that receipt to a text
    file, and turn itself into a CSV row for exports.
    """

    def __init__(self, payment_id, plate_number, vehicle_type, slot_id,
                 entry_time, exit_time, amount):
        self.__payment_id = payment_id
        self.__plate_number = plate_number
        self.__vehicle_type = vehicle_type
        self.__slot_id = slot_id
        self.__entry_time = entry_time
        self.__exit_time = exit_time
        self.__amount = amount

    @property
    def payment_id(self):
        return self.__payment_id

    @property
    def plate_number(self):
        return self.__plate_number

    @property
    def vehicle_type(self):
        return self.__vehicle_type

    @property
    def slot_id(self):
        return self.__slot_id

    @property
    def entry_time(self):
        return self.__entry_time

    @property
    def exit_time(self):
        return self.__exit_time

    @property
    def amount(self):
        return self.__amount

    @property
    def duration(self):
        """Time parked, formatted as 'Hh Mm'."""
        minutes = int((self.__exit_time - self.__entry_time).total_seconds() // 60)
        return f"{minutes // 60}h {minutes % 60}m"

    def receipt_text(self):
        return "\n".join([
            "------- PARKING RECEIPT -------",
            f"Receipt No : {self.__payment_id}",
            f"Vehicle    : {self.__plate_number} ({self.__vehicle_type})",
            f"Slot       : {self.__slot_id}",
            f"Entry      : {self.__entry_time:{TIME_FORMAT}}",
            f"Exit       : {self.__exit_time:{TIME_FORMAT}}",
            f"Duration   : {self.duration}",
            f"Amount     : Rs. {self.__amount:.2f}",
            "-------------------------------",
        ])

    def save_receipt(self, folder):
        """Write the receipt to <folder>/receipt_<id>.txt and return the path."""
        os.makedirs(folder, exist_ok=True)
        path = os.path.join(folder, f"receipt_{self.__payment_id}.txt")
        with open(path, "w", encoding="utf-8") as f:
            f.write(self.receipt_text() + "\n")
        return path

    def to_csv_row(self):
        return [self.__payment_id, self.__plate_number, self.__vehicle_type,
                self.__slot_id, f"{self.__entry_time:{TIME_FORMAT}}",
                f"{self.__exit_time:{TIME_FORMAT}}", f"{self.__amount:.2f}"]

    @classmethod
    def from_row(cls, row):
        """Build a Payment from a database row (see ParkingLot queries)."""
        return cls(row["payment_id"], row["plate_number"], row["vehicle_type"],
                   row["slot_id"], datetime.fromisoformat(row["entry_time"]),
                   datetime.fromisoformat(row["exit_time"]), row["amount"])
