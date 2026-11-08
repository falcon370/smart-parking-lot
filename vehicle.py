"""Vehicle hierarchy: an abstract Vehicle with Car and Bike subclasses.

OOP concepts shown here:
    Abstraction    Vehicle is an abstract base class; it defines *what* every
                   vehicle must provide without saying *how*.
    Inheritance    Car and Bike inherit validation and helpers from Vehicle.
    Overriding     Each subclass overrides calculate_fee() with its own tariff.
    Polymorphism   Code that holds "a Vehicle" calls calculate_fee() and gets
                   the right behaviour for a car or a bike automatically.
    Encapsulation  Plate number and owner are private and validated on update.
"""

import math
import re
from abc import ABC, abstractmethod

from exceptions import InvalidInputError

# Plate numbers: 4-12 characters, upper-case letters, digits and hyphens only.
PLATE_PATTERN = re.compile(r"^[A-Z0-9-]{4,12}$")
MAX_OWNER_LENGTH = 50


class Vehicle(ABC):
    """Abstract base class for every vehicle that can use the parking lot.

    A Vehicle cannot be created directly (``Vehicle("KA01")`` raises
    TypeError). Subclasses must implement ``vehicle_type``, ``hourly_rate``
    and ``calculate_fee``.

    Attributes:
        plate_number (str): Registration number, stored in upper case.
        owner (str): Owner's name; may be empty.
    """

    def __init__(self, plate_number, owner=""):
        """Create a vehicle.

        Args:
            plate_number: Registration number, e.g. "KA01AB1234".
            owner: Optional owner name.

        Raises:
            InvalidInputError: If the plate or owner name is invalid.
        """
        # Assign through the property setters so validation always runs.
        self.plate_number = plate_number
        self.owner = owner

    # ------------------------------------------------------------------
    # Encapsulated attributes (private storage + validating setters)
    # ------------------------------------------------------------------
    @property
    def plate_number(self):
        """str: The vehicle's registration number (upper case)."""
        return self.__plate_number

    @plate_number.setter
    def plate_number(self, value):
        """Validate and store a plate number; the old value is kept on error."""
        plate = str(value).strip().upper()
        if not PLATE_PATTERN.match(plate):
            raise InvalidInputError(
                "Plate number must be 4-12 characters: letters, digits or '-'."
            )
        self.__plate_number = plate

    @property
    def owner(self):
        """str: The owner's name, or an empty string if not given."""
        return self.__owner

    @owner.setter
    def owner(self, value):
        """Validate and store an owner name (letters, spaces, '.' and ''' only)."""
        name = str(value).strip()
        if len(name) > MAX_OWNER_LENGTH:
            raise InvalidInputError(
                f"Owner name must be at most {MAX_OWNER_LENGTH} characters."
            )
        if name and not all(ch.isalpha() or ch in " .'" for ch in name):
            raise InvalidInputError("Owner name may only contain letters and spaces.")
        self.__owner = name

    # ------------------------------------------------------------------
    # Abstract interface - every subclass must implement these
    # ------------------------------------------------------------------
    @property
    @abstractmethod
    def vehicle_type(self):
        """str: Type name; must match a ParkingSlot.slot_type ('car'/'bike')."""

    @property
    @abstractmethod
    def hourly_rate(self):
        """int: Charge in rupees for each started hour."""

    @abstractmethod
    def calculate_fee(self, entry_time, exit_time):
        """Calculate the parking fee for one stay.

        Args:
            entry_time (datetime): When the vehicle entered.
            exit_time (datetime): When the vehicle left.

        Returns:
            int: Fee in rupees.
        """

    # ------------------------------------------------------------------
    # Shared helpers inherited by all subclasses
    # ------------------------------------------------------------------
    @staticmethod
    def billable_hours(entry_time, exit_time):
        """Return the number of hours to charge.

        Every started hour counts as a full hour, with a minimum of one hour:
        0-60 min -> 1, 61-120 min -> 2, and so on.

        Raises:
            InvalidInputError: If exit_time is before entry_time.
        """
        seconds = (exit_time - entry_time).total_seconds()
        if seconds < 0:
            raise InvalidInputError("Exit time cannot be before entry time.")
        return max(1, math.ceil(seconds / 3600))

    def __str__(self):
        """Readable form, e.g. 'Car KA01AB1234, owner Ravi Kumar'."""
        owner = f", owner {self.owner}" if self.owner else ""
        return f"{self.vehicle_type.title()} {self.plate_number}{owner}"


class Car(Vehicle):
    """A car. Tariff: Rs. 20 per started hour, no daily cap."""

    @property
    def vehicle_type(self):
        return "car"

    @property
    def hourly_rate(self):
        return 20

    def calculate_fee(self, entry_time, exit_time):
        """Override: billable hours x Rs. 20."""
        return self.billable_hours(entry_time, exit_time) * self.hourly_rate


class Bike(Vehicle):
    """A bike. Tariff: Rs. 10 per started hour, capped at Rs. 100 per day."""

    DAILY_CAP = 100  # maximum charge for any 24-hour period

    @property
    def vehicle_type(self):
        return "bike"

    @property
    def hourly_rate(self):
        return 10

    def calculate_fee(self, entry_time, exit_time):
        """Override: Rs. 10 per hour, but never more than Rs. 100 per day.

        Example: 26 hours = 1 full day (Rs. 100) + 2 hours (Rs. 20) = Rs. 120.
        """
        hours = self.billable_hours(entry_time, exit_time)
        full_days, extra_hours = divmod(hours, 24)
        return (full_days * self.DAILY_CAP
                + min(extra_hours * self.hourly_rate, self.DAILY_CAP))


# Registry mapping the type name stored in the database to its class.
# Add new vehicle types here so the menu and the database can use them.
VEHICLE_CLASSES = {"car": Car, "bike": Bike}


def create_vehicle(vehicle_type, plate_number, owner=""):
    """Factory function: build the right Vehicle subclass from a type name.

    Args:
        vehicle_type: 'car' or 'bike' (case-insensitive).
        plate_number: Registration number.
        owner: Optional owner name.

    Returns:
        Vehicle: A Car or Bike instance.

    Raises:
        InvalidInputError: If the type is unknown or the data is invalid.
    """
    key = str(vehicle_type).strip().lower()
    if key not in VEHICLE_CLASSES:
        raise InvalidInputError(
            f"Unknown vehicle type '{vehicle_type}'. Choose: {', '.join(VEHICLE_CLASSES)}."
        )
    return VEHICLE_CLASSES[key](plate_number, owner)
