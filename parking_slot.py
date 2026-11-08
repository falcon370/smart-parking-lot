"""A single parking space in the lot.

OOP concept shown here:
    Encapsulation  A slot's id, type and occupied flag are private and
                   read-only. The occupied flag can only change through
                   occupy() and free(), which reject invalid changes.
"""

from exceptions import InvalidInputError, SlotStateError

# The kinds of slot the lot has; each matches a Vehicle.vehicle_type.
SLOT_TYPES = ("car", "bike")


class ParkingSlot:
    """One parking space that holds at most one vehicle.

    Attributes (read-only):
        slot_id (int): Unique slot number, starting at 1.
        slot_type (str): 'car' or 'bike'.
        is_occupied (bool): True while a vehicle is parked here.
    """

    def __init__(self, slot_id, slot_type, is_occupied=False):
        """Create a slot.

        Args:
            slot_id: Positive whole number.
            slot_type: One of SLOT_TYPES.
            is_occupied: Initial state, used when loading from the database.

        Raises:
            InvalidInputError: If slot_id or slot_type is invalid.
        """
        if not isinstance(slot_id, int) or slot_id <= 0:
            raise InvalidInputError("Slot id must be a positive whole number.")
        if slot_type not in SLOT_TYPES:
            raise InvalidInputError(f"Slot type must be one of {SLOT_TYPES}.")
        self.__slot_id = slot_id
        self.__slot_type = slot_type
        self.__is_occupied = bool(is_occupied)

    # Read-only properties: there are no setters, so assigning raises AttributeError.
    @property
    def slot_id(self):
        return self.__slot_id

    @property
    def slot_type(self):
        return self.__slot_type

    @property
    def is_occupied(self):
        return self.__is_occupied

    def can_fit(self, vehicle):
        """Return True if this slot is free and meant for this vehicle's type."""
        return not self.__is_occupied and self.__slot_type == vehicle.vehicle_type

    def occupy(self):
        """Mark the slot as taken.

        Raises:
            SlotStateError: If the slot is already occupied.
        """
        if self.__is_occupied:
            raise SlotStateError(f"Slot {self.__slot_id} is already occupied.")
        self.__is_occupied = True

    def free(self):
        """Mark the slot as empty.

        Raises:
            SlotStateError: If the slot is already free.
        """
        if not self.__is_occupied:
            raise SlotStateError(f"Slot {self.__slot_id} is already free.")
        self.__is_occupied = False

    def __str__(self):
        """Readable form, e.g. 'Slot 3 (car): free'."""
        status = "occupied" if self.__is_occupied else "free"
        return f"Slot {self.__slot_id} ({self.__slot_type}): {status}"
