from datetime import date, datetime
import decimal


class Boolean:
    @classmethod
    def __call__(cls, instance, value):
        return bool(value)


class Decimal:
    def __init__(self, places):
        self.places = places

    def __call__(self, instance, value):
        return round(decimal.Decimal(value), self.places)

    def serialize(self, value):
        return f"{value:>.{self.places}f}"


class ISODate:
    @classmethod
    def __call__(cls, instance, value):
        if not isinstance(value, date):
            value = datetime.strptime(value, "%Y-%m-%d").date()
        return value

    @classmethod
    def serialize(cls, value):
        return value.isoformat()


class Set:
    def __init__(self, *args, name=None):
        self.valid = args
        if name:
            self.__name__ = name

    def __call__(self, instance, value):
        if value not in self.valid:
            raise ValueError(f"must be one of {self.valid}")
        return value
