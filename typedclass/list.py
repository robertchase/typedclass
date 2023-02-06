"""List Type"""
import json

from typedclass.typed import Typed, InvalidNestedTyped


class ListTooShortError(ValueError):
    def __init__(self, min):
        self.args = (f"length must be at least {min}",)


class ListTooLongError(ValueError):
    def __init__(self, max):
        self.args = (f"length must be no more than {max}",)


class ListDuplicateItemError(ValueError):
    def __init__(self, value):
        self.args = (f"{value} already in list",)


class List:
    """support a list as a Field type"""
    def __init__(self, element_type, min=0, max=0, allow_dups=True):
        self.type = element_type
        self.is_nested = False
        self.min = min
        self.max = max
        self.allow_dups = allow_dups

        if isinstance(self.type, type):
            if issubclass(self.type, Typed):
                self.is_nested = True
            else:
                self.type = self.type()

    def __call__(self, value):
        return _List(self, value)

    def serialize(self, value):
        return value.serialize()


class _List:
    """List instance"""
    def __init__(self, parent, value):
        self.type = parent.type
        self.is_nested = parent.is_nested
        self.min = parent.min
        self.max = parent.max
        self.allow_dups = parent.allow_dups

        if isinstance(value, str):
            value = json.loads(value)
        if not isinstance(value, list):
            raise Exception("expecting a list")
        if self.min > 0:
            if len(value) < self.min:
                raise ListTooShortError(self.min)
        if self.max > 0:
            if len(value) > self.max:
                raise ListTooLongError(self.max)

        self.store = []
        for item in value:
            self.append(item)

    def _parse(self, item):
        if self.is_nested:
            if isinstance(item, dict):
                item = self.type(**item)
            elif not isinstance(item, self.type):
                raise InvalidNestedTyped(self.type)
        else:
            item = self.type(item)
        return item

    def serialize(self):
        if self.is_nested:
            value = [item.as_dict() for item in self.store]
        elif serializer := getattr(self.type, "serialize", None):
            value = [serializer(item) for item in self.store]
        else:
            value = self.store.copy()
        value = json.dumps(value)
        return value

    def __len__(self):
        return len(self.store)

    def __eq__(self, other):
        return self.store == other

    def __getitem__(self, key):
        return self.store[key]

    def __setitem__(self, key, value):
        value = self._parse(value)
        if not self.allow_dups:
            if self.store.count(value) != 0 and self.store[key] != value:
                raise ListDuplicateItemError(value)
        self.store[key] = value

    def __delitem__(self, key):
        if self.min > 0:
            # preflight length check (key is an arbitrary slice)
            temp = [0] * len(self.store)
            del temp[key]
            if len(temp) < self.min:
                raise ListTooShortError(self.min)
        del self.store[key]

    def append(self, value):
        if self.max > 0:
            if len(self.store) == self.max:
                raise ListTooLongError(self.max)
        value = self._parse(value)
        if not self.allow_dups and value in self.store:
            raise ListDuplicateItemError(value)
        self.store.append(value)

    def index(self, *args, **kwargs):
        return self.store.index(*args, **kwargs)
