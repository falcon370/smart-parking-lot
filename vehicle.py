import math
from abc import ABC, abstractmethod


class Vehicle(ABC):  # Abstraction
    def __init__(self, plate_number, owner=""):
        self.plate_number = plate_number
        self.owner = owner

    @property
    @abstractmethod
    def vehicle_type(self):
        ...

    @abstractmethod
    def calculate_fee(self, entry_time, exit_time):
        ...

    @staticmethod
    def _hours(entry_time, exit_time):
        seconds = (exit_time - entry_time).total_seconds()
        return max(1, math.ceil(seconds / 3600))  # minimum 1 hour


class Car(Vehicle):  # Inheritance
    vehicle_type = "car"
    RATE = 20  # per hour

    def calculate_fee(self, entry_time, exit_time):  # Polymorphism
        return self._hours(entry_time, exit_time) * self.RATE


class Bike(Vehicle):
    vehicle_type = "bike"
    RATE = 10  # per hour

    def calculate_fee(self, entry_time, exit_time):
        return self._hours(entry_time, exit_time) * self.RATE


VEHICLE_CLASSES = {"car": Car, "bike": Bike}
