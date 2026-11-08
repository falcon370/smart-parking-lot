"""A single parking space in the lot."""

from exceptions import InvalidInputError, SlotStateError

SLOT_TYPES = ("car", "bike")


class ParkingSlot:
    """One parking space.

    Encapsulation: the occupied flag is private and read-only from outside.
    It only changes through occupy() and free(), which refuse invalid
    changes (parking in a taken slot, or freeing an empty one).
    """

    def __init__(self, slot_id, slot_type, is_occupied=False):
        if not isinstance(slot_id, int) or slot_id <= 0:
            raise InvalidInputError("Slot id must be a positive whole number.")
        if slot_type not in SLOT_TYPES:
            raise InvalidInputError(f"Slot type must be one of {SLOT_TYPES}.")
        self.__slot_id = slot_id
        self.__slot_type = slot_type
        self.__is_occupied = bool(is_occupied)

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
        """True if this slot is free and meant for this kind of vehicle."""
        return not self.__is_occupied and self.__slot_type == vehicle.vehicle_type

    def occupy(self):
        if self.__is_occupied:
            raise SlotStateError(f"Slot {self.__slot_id} is already occupied.")
        self.__is_occupied = True

    def free(self):
        if not self.__is_occupied:
            raise SlotStateError(f"Slot {self.__slot_id} is already free.")
        self.__is_occupied = False

    def __str__(self):
        status = "occupied" if self.__is_occupied else "free"
        return f"Slot {self.__slot_id} ({self.__slot_type}): {status}"
