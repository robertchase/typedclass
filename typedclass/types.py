from datetime import date, datetime
import decimal


class Boolean:
    @classmethod
    def __call__(cls, instance, value):
        return bool(value)


class Decimal:
    def __init__(self, precision):
        self.precision = int(precision)

    def __call__(self, instance, value):
        return round(decimal.Decimal(value), self.precision)

    def serialize(self, value):
        return f"{value:>.{self.precision}f}"


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


class String:
    def __init__(self, min=0, max=None):
        self.min = int(min)
        if max:
            max = int(max)
            if max < 1:
                raise AttributeError("max ({max}) must be greater than 0")
        self.max = max

    def __call__(self, instance, value):
        value = str(value)
        if self.min:
            if len(value) < self.min:
                raise ValueError(f"length is less than minimum ({self.min})")
        if self.max:
            if len(value) > self.max:
                raise ValueError(f"length is longer than maximum({self.max})")
        return value
