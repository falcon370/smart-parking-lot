"""A completed parking payment and its receipt.

File handling shown here:
    save_receipt()  writes each receipt to a text file (receipts/receipt_N.txt)
    to_csv_row()    supplies rows for the payments.csv export
"""

import os
from datetime import datetime

TIME_FORMAT = "%Y-%m-%d %H:%M:%S"

# Column order for payments.csv; must match Payment.to_csv_row().
CSV_HEADER = ["payment_id", "plate_number", "vehicle_type", "slot_id",
              "entry_time", "exit_time", "amount"]


class Payment:
    """One finished parking session that has been paid for.

    Payment objects are created by ParkingLot when a vehicle leaves, or
    rebuilt from the database for the payment history. All data is private
    and read-only, because a payment must not change once it is recorded.

    Attributes (read-only):
        payment_id (int): Receipt number (database id).
        plate_number (str): Vehicle that paid.
        vehicle_type (str): 'car' or 'bike'.
        slot_id (int): Slot the vehicle used.
        entry_time (datetime): Time of entry.
        exit_time (datetime): Time of exit.
        amount (float): Fee charged in rupees.
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
        """str: Time parked, e.g. '2h 15m'."""
        minutes = int((self.__exit_time - self.__entry_time).total_seconds() // 60)
        return f"{minutes // 60}h {minutes % 60}m"

    def receipt_text(self):
        """Return the receipt as a multi-line string, ready to print or save."""
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
        """Write the receipt to ``<folder>/receipt_<id>.txt``.

        The folder is created if it does not exist.

        Returns:
            str: Path of the file written.

        Raises:
            OSError: If the file cannot be written.
        """
        os.makedirs(folder, exist_ok=True)
        path = os.path.join(folder, f"receipt_{self.__payment_id}.txt")
        with open(path, "w", encoding="utf-8") as f:
            f.write(self.receipt_text() + "\n")
        return path

    def to_csv_row(self):
        """Return this payment as a list of values in CSV_HEADER order."""
        return [self.__payment_id, self.__plate_number, self.__vehicle_type,
                self.__slot_id, f"{self.__entry_time:{TIME_FORMAT}}",
                f"{self.__exit_time:{TIME_FORMAT}}", f"{self.__amount:.2f}"]

    @classmethod
    def from_row(cls, row):
        """Alternative constructor: build a Payment from a database row.

        Args:
            row: sqlite3.Row with the columns listed in CSV_HEADER, with
                times stored as ISO strings.
        """
        return cls(row["payment_id"], row["plate_number"], row["vehicle_type"],
                   row["slot_id"], datetime.fromisoformat(row["entry_time"]),
                   datetime.fromisoformat(row["exit_time"]), row["amount"])
