"""Typed Class System"""
from typedclass.field import Field


class Kwargs:
    """a 'Field' to scoop up remaining keyword arguments"""


class ReservedAttributeError(AttributeError):
    def __init__(self, name):
        self.args = (f"reserved attribute: {name}",)


class RequiredAttributeError(AttributeError):
    def __init__(self, name):
        self.args = (f"missing required attribute: {name}",)


class ExtraAttributeError(AttributeError):
    def __init__(self, name):
        self.args = (f"extra attribute(s): {', '.join(name)}",)


class DuplicateAttributeError(AttributeError):
    def __init__(self, name):
        self.args = (f"duplicate attribute: {name}",)


class ReadOnlyFieldError(ValueError):
    """custom exception"""


class NoneValueError(ValueError):
    def __init__(self, name):
        self.args = (f"field cannot be null: {name}",)


class InvalidNestedTyped(ValueError):
    def __init__(self, typed_class):
        self.args = (f"expecting {typed_class}",)


class ListTooShortError(ValueError):
    def __init__(self, min):
        self.args = (f"length must be at least {min}",)


class ListTooLongError(ValueError):
    def __init__(self, max):
        self.args = (f"length must be no more than {max}",)


class ListDuplicateItemError(ValueError):
    def __init__(self, value):
        self.args = (f"{value} already in list",)


class _Model(type):
    """metaclass for typed class

       the metaclass digests the fields
    """

    def __new__(cls, name, supers, attrs):

        fields = {}

        def add_fields(source):
            for key, value in source.items():
                if isinstance(value, Field):
                    if key in RESERVED:
                        raise ReservedAttributeError(key)
                    if isinstance(value.type, type):
                        if issubclass(value.type, Typed):
                            value.is_nested = True
                        else:
                            value.type = value.type()
                    value.name = key
                    fields[key] = value

        # grab super-class Fields
        for sup in supers[::-1]:
            if issubclass(sup, Typed):
                # look in "_f" so we get the super's supers too
                for fld in sup.__dict__["_f"]:
                    fields[fld.name] = fld
            else:
                add_fields(sup.__dict__)
        # add/overlay Fields from this class
        add_fields(attrs)

        # look for Kwargs
        attrs["_k"] = None
        for sup in supers[::-1]:
            if issubclass(sup, Typed):
                attrs["_k"] = sup.__dict__["_k"]
        for key, value in attrs.items():
            if isinstance(value, Kwargs):
                attrs["_k"] = key

        # --- create the "_f" attribute to hold shared field list
        attrs["_f"] = [field for field in fields.values()]

        return super().__new__(cls, name, supers, attrs)


class Typed(metaclass=_Model):
    """base typed class

       Notes:
           1. The Typed's fields are kept in the "_f" attribute and the
              instance values are kept in the "_v" attribute. The "_f"
              attribute is shared with all instances.
           2. Type Typed's "_k" attribute holds the name (or None) of a
              catch-all dict for any unspecified fields.
    """

    def __init__(self, *args, **kwargs):
        self.__dict__["_v"] = {}
        if self._k:
            self._v[self._k] = {}

        if len(args) > len(self._f):
            raise ExtraAttributeError(args[len(self._f):])

        for value, field in zip(args, self._f):
            if field.name in kwargs:
                raise DuplicateAttributeError(field.name)
            kwargs[field.name] = value  # convert args to kwargs

        for name in kwargs.keys():
            try:
                self._lookup_field(name)  # look for undefined fields
            except AttributeError as err:
                if self._k:
                    self._v[self._k][name] = kwargs[name]
                else:
                    err.args = (f"undefined field name '{name}'",)
                    raise

        for field in self._f:
            if field.is_required:
                if field.default == Field.NO_DEFAULT:
                    if field.name not in kwargs:
                        raise RequiredAttributeError(field.name)
            if field.default != Field.NO_DEFAULT:
                if field.name not in kwargs:
                    kwargs[field.name] = field.default

        for field in self._f:
            if field.name in kwargs:
                self._setfield(field, kwargs[field.name])
                field.after_init(self)

        self.__after_init__()

    def __after_init__(self):
        pass

    def __str__(self):
        return str(self.as_dict())

    def as_dict(self, serialize=True):
        result = {}
        if self._k:
            result[self._k] = self._v[self._k]
        for field in self._f:
            if field.name in self._v:
                value = self._v[field.name]
                if value and serialize:
                    if field.is_nested:
                        value = value.as_dict()
                    elif serializer := getattr(field.type, "serialize", None):
                        value = serializer(value)
                result[field.name] = value
        return result

    @classmethod
    def from_dict(cls, data):

        def _from_dict(data):
            return cls(**{
                f.name: data[f.name]
                for f in cls._f
                if f.name in data  # ignore keys that aren't field names
            })

        if data:
            if isinstance(data, list):
                result = [_from_dict(item) for item in data]
            else:
                result = _from_dict(data)
        else:
            result = None
        return result

    def __getattribute__(self, name):
        value = object.__getattribute__(self, name)
        if isinstance(value, Field):
            if name not in self._v:
                raise AttributeError(name)
            value = self._v[name]
        if isinstance(value, Kwargs):
            value = self._v[self._k]

        return value

    def __setattr__(self, name, value):
        field = self._lookup_field(name)
        value = field.before_set(self, value)
        if field.is_readonly:
            raise ReadOnlyFieldError(name)
        self._setfield(field, value)
        field.after_set(self)

    def _lookup_field(self, name):
        field = object.__getattribute__(self, name)
        if not isinstance(field, Field):
            raise AttributeError(name)
        return field

    def _setfield(self, field, value):
        if value is None:
            if field.default is None:
                self._v[field.name] = None
                return
            else:
                raise NoneValueError(field.name)

        try:
            if field.is_nested:
                if isinstance(value, dict):
                    value = field.type(**value)
                elif not isinstance(value, field.type):
                    raise InvalidNestedTyped(field.type)
            else:
                value = field.parse(self, value)
            self._v[field.name] = value
        except ValueError as err:
            if hasattr(field.type, "__name__"):
                type = field.type.__name__
            else:
                type = field.type.__class__.__name__
            error = (
                f"invalid <{type}> value ({value}) for field '{field.name}'"
                f": {str(err)}"
            )
            err.args = (error,)
            raise

    def __delattr__(self, name):
        field = self._lookup_field(name)
        if field.is_required:
            raise AttributeError("cannot delete a required field")
        del self._v[name]


class List:
    """support a list as a Field type"""
    def __init__(self, element_type, min=0, max=0, allow_dups=True):
        self.type = element_type
        self.min = min
        self.max = max
        self.allow_dups = allow_dups

    def __call__(self, instance, value):
        return _List(self, value)

    def serialize(self, value):
        return value.serialize()


class _List:
    def __init__(self, parent, value):
        self.type = parent.type
        self.is_nested = False
        self.min = parent.min
        self.max = parent.max
        self.allow_dups = parent.allow_dups

        if isinstance(self.type, type):
            if issubclass(self.type, Typed):
                self.is_nested = True
            else:
                self.type = self.type()

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
        # self.store = [self._parse(item) for item in value]

    def _parse(self, item):
        if self.is_nested:
            if isinstance(item, dict):
                item = self.type(**item)
            elif not isinstance(item, self.type):
                raise InvalidNestedTyped(self.type)
        else:
            item = self.type(None, item)
        return item

    def serialize(self):
        if self.is_nested:
            value = [item.as_dict() for item in self.store]
        elif serializer := getattr(self.type, "serialize", None):
            value = [serializer(item) for item in self.store]
        else:
            value = self.store.copy()
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
            temp = self.store.copy()
            del temp[key]
            if value in temp:
                raise ListDuplicateItemError(value)
        self.store[key] = value

    def __delitem__(self, key):
        if self.min > 0:
            # preflight check (key is an arbitrary slice)
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


RESERVED = dir(Typed)
