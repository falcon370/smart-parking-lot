"""Vehicle hierarchy: an abstract Vehicle with Car and Bike subclasses."""

import math
import re
from abc import ABC, abstractmethod

from exceptions import InvalidInputError

PLATE_PATTERN = re.compile(r"^[A-Z0-9-]{4,12}$")
MAX_OWNER_LENGTH = 50


class Vehicle(ABC):
    """Abstract base class for every vehicle that can use the lot.

    Abstraction: Vehicle cannot be created directly. Each subclass must say
    what type it is and how its parking fee is calculated.
    Encapsulation: plate number and owner are private and are only changed
    through validating property setters.
    """

    def __init__(self, plate_number, owner=""):
        self.plate_number = plate_number  # goes through the setter below
        self.owner = owner

    # ---- encapsulated attributes ----
    @property
    def plate_number(self):
        return self.__plate_number

    @plate_number.setter
    def plate_number(self, value):
        plate = str(value).strip().upper()
        if not PLATE_PATTERN.match(plate):
            raise InvalidInputError(
                "Plate number must be 4-12 characters: letters, digits or '-'."
            )
        self.__plate_number = plate

    @property
    def owner(self):
        return self.__owner

    @owner.setter
    def owner(self, value):
        name = str(value).strip()
        if len(name) > MAX_OWNER_LENGTH:
            raise InvalidInputError(
                f"Owner name must be at most {MAX_OWNER_LENGTH} characters."
            )
        if name and not all(ch.isalpha() or ch in " .'" for ch in name):
            raise InvalidInputError("Owner name may only contain letters and spaces.")
        self.__owner = name

    # ---- abstract interface ----
    @property
    @abstractmethod
    def vehicle_type(self):
        """Short type name, matching ParkingSlot.slot_type ('car' or 'bike')."""

    @property
    @abstractmethod
    def hourly_rate(self):
        """Parking charge per started hour, in rupees."""

    @abstractmethod
    def calculate_fee(self, entry_time, exit_time):
        """Return the fee for parking between entry_time and exit_time."""

    # ---- shared helpers ----
    @staticmethod
    def billable_hours(entry_time, exit_time):
        """Hours to charge: every started hour counts, minimum one hour."""
        seconds = (exit_time - entry_time).total_seconds()
        if seconds < 0:
            raise InvalidInputError("Exit time cannot be before entry time.")
        return max(1, math.ceil(seconds / 3600))

    def __str__(self):
        owner = f", owner {self.owner}" if self.owner else ""
        return f"{self.vehicle_type.title()} {self.plate_number}{owner}"


class Car(Vehicle):
    """A car: Rs. 20 per started hour."""

    @property
    def vehicle_type(self):
        return "car"

    @property
    def hourly_rate(self):
        return 20

    def calculate_fee(self, entry_time, exit_time):  # overrides Vehicle
        return self.billable_hours(entry_time, exit_time) * self.hourly_rate


class Bike(Vehicle):
    """A bike: Rs. 10 per started hour, capped at Rs. 100 per day."""

    DAILY_CAP = 100

    @property
    def vehicle_type(self):
        return "bike"

    @property
    def hourly_rate(self):
        return 10

    def calculate_fee(self, entry_time, exit_time):  # overrides Vehicle
        hours = self.billable_hours(entry_time, exit_time)
        full_days, extra_hours = divmod(hours, 24)
        return (full_days * self.DAILY_CAP
                + min(extra_hours * self.hourly_rate, self.DAILY_CAP))


# Maps the type name stored in the database to the class that handles it.
VEHICLE_CLASSES = {"car": Car, "bike": Bike}


def create_vehicle(vehicle_type, plate_number, owner=""):
    """Factory: build the right Vehicle subclass from a type name."""
    key = str(vehicle_type).strip().lower()
    if key not in VEHICLE_CLASSES:
        raise InvalidInputError(
            f"Unknown vehicle type '{vehicle_type}'. Choose: {', '.join(VEHICLE_CLASSES)}."
        )
    return VEHICLE_CLASSES[key](plate_number, owner)
