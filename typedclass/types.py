from datetime import date, datetime
import decimal
import json
import re


class Boolean:
    @classmethod
    def __call__(cls, instance, value):
        if value in (True, 1, "1"):
            value = True
        elif value in (False, 0, "0"):
            value = False
        else:
            raise ValueError(f"expecting bool value, got {value}")
        return value


class Decimal:
    def __init__(self, precision):
        self.precision = int(precision)

    def __call__(self, instance, value):
        try:
            return round(decimal.Decimal(value), self.precision)
        except decimal.InvalidOperation as exc:
            raise ValueError(str(exc))

    def serialize(self, value):
        return f"{value:>.{self.precision}f}"


class Integer:
    @classmethod
    def __call__(cls, instance, value):
        if not re.match(r"\d+$", str(value)):
            raise ValueError("not an integer")
        return int(value)


class ISODate:
    @classmethod
    def __call__(cls, instance, value):
        if not isinstance(value, date):
            try:
                value = datetime.strptime(value, "%Y-%m-%d").date()
            except TypeError as err:
                raise ValueError(err) from err
        return value

    @classmethod
    def serialize(cls, value):
        return value.isoformat()


class ISODateTime:
    @classmethod
    def __call__(cls, instance, value):
        if not isinstance(value, datetime):
            try:
                value = datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
            except TypeError as err:
                raise ValueError(err) from err
        return value

    @classmethod
    def serialize(cls, value):
        return value.isoformat()


class Json:

    @classmethod
    def __call__(self, instance, value):
        if isinstance(value, str):
            try:
                value = json.loads(value)
            except json.decoder.JSONDecodeError as exc:
                raise ValueError(exc) from exc
        return value

    @classmethod
    def serialize(cls, value):
        return json.dumps(value)


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
