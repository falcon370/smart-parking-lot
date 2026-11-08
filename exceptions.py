"""Custom exceptions for the parking lot system.

Every error the application raises on purpose derives from ParkingError,
so the menu can catch them all with a single ``except ParkingError``.
"""


class ParkingError(Exception):
    """Base class for all parking lot errors."""


class InvalidInputError(ParkingError):
    """Raised when user-supplied data fails validation."""


class SlotUnavailableError(ParkingError):
    """Raised when no free slot of the required type exists."""


class SlotStateError(ParkingError):
    """Raised when a slot is occupied twice or freed while already free."""


class VehicleAlreadyParkedError(ParkingError):
    """Raised when a vehicle that is already parked tries to park again."""


class VehicleNotFoundError(ParkingError):
    """Raised when removing a vehicle that has no active parking record."""
