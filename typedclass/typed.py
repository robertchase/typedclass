"""Typed Class System"""
import json

from typedclass.field import Field


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


class _Model(type):
    """metaclass for typed class

       the metaclass digests the fields
    """

    def __new__(cls, name, supers, attrs):

        fields = {}

        def update_fields(data):
            for key, value in data.items():
                if isinstance(value, Field):
                    if key in RESERVED:
                        raise ReservedAttributeError(key)
                    value.name = key
                    fields[key] = value  # will over-write/ride parent Fields

        for sup in supers[::-1]:  # move up through class hierarchy
            update_fields(sup.__dict__)
        update_fields(attrs)

        # --- create the "_f" attribute to hold shared field list
        attrs["_f"] = [field for field in fields.values()]

        return super().__new__(cls, name, supers, attrs)


class Typed(metaclass=_Model):
    """base typed class

       Notes:
           1. The Typed's fields are kept in the "_f" attribute and the
              instance values are kept in the "_v" attribute. The "_f"
              attribute is shared with all instances.
    """

    def __init__(self, *args, **kwargs):
        self.__dict__["_v"] = {}

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
        for field in self._f:
            if field.name in self._v:
                value = self._v[field.name]
                if value and serialize:
                    if serializer := getattr(field.type, "serialize", None):
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

    def dumps(self):
        return json.dumps(self.as_dict())

    @classmethod
    def loads(cls, data):
        return cls(**json.loads(data))

    def __getattribute__(self, name):
        value = object.__getattribute__(self, name)
        if isinstance(value, Field):
            if name not in self._v:
                raise AttributeError(name)
            value = self._v[name]

        return value

    def __setattr__(self, name, value):
        field = self._lookup_field(name)
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
            self._v[field.name] = field.parse(self, value)
        except ValueError as err:
            if hasattr(field.type, "__name__"):
                type = field.type.__name__
            else:
                type = field.type.__class__.__name__
            error = (
                f"invalid <{type}> value ({value}) for field '{field.name}'"
            )
            err.args = (error,)
            raise

    def __delattr__(self, name):
        field = self._lookup_field(name)
        if field.is_required:
            raise AttributeError("cannot delete a required field")
        del self._v[name]


RESERVED = dir(Typed)
