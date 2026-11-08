class ParkingSlot:
    def __init__(self, slot_id, slot_type, is_occupied=False):
        self.slot_id = slot_id
        self.slot_type = slot_type
        self.is_occupied = is_occupied

    def occupy(self):
        self.is_occupied = True

    def free(self):
        self.is_occupied = False

    def __str__(self):
        status = "occupied" if self.is_occupied else "free"
        return f"Slot {self.slot_id} ({self.slot_type}): {status}"
