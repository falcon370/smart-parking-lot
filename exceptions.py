"""Custom exceptions for the parking lot system.

Every error the application raises on purpose inherits from ParkingError,
so the menu in main.py can handle all of them with one ``except ParkingError``
while still letting each part of the code raise a specific, meaningful error.

Hierarchy:
    ParkingError
    ├── InvalidInputError          bad plate, owner, vehicle type, slot data
    ├── SlotUnavailableError       no free slot of the needed type
    ├── SlotStateError             occupy a taken slot / free an empty one
    ├── VehicleAlreadyParkedError  same plate parked twice
    └── VehicleNotFoundError       removing a vehicle that is not parked
"""


class ParkingError(Exception):
    """Base class for all errors raised by the parking lot system."""


class InvalidInputError(ParkingError):
    """User-supplied data failed validation (plate, owner, type, slot)."""


class SlotUnavailableError(ParkingError):
    """No free slot of the required vehicle type is left in the lot."""


class SlotStateError(ParkingError):
    """A slot was occupied while already taken, or freed while already free."""


class VehicleAlreadyParkedError(ParkingError):
    """A vehicle tried to park while it already has an active parking record."""


class VehicleNotFoundError(ParkingError):
    """A vehicle was removed but it has no active parking record."""
