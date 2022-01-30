"""Typed Class System"""
from typedclass.field import Field


class RequiredAttributeError(AttributeError):
    """custom exception"""


class ReadOnlyFieldError(ValueError):
    """custom exception"""


class NoneValueError(ValueError):
    """custom exception"""


class _Model(type):
    """metaclass for typed class

       the metaclass digests the fields
    """

    def __new__(cls, name, supers, attrs):

        # --- create the "_f" attribute to hold shared field list
        fields = attrs["_f"] = []

        def update_fields(data):
            for key, value in data.items():
                if isinstance(value, Field):
                    value.name = key
                    fields.append(value)

        for sup in supers[::-1]:
            update_fields(sup.__dict__)
        update_fields(attrs)

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

        for value, field in zip(args, self._f):
            kwargs[field.name] = value

        for field in self._f:
            if field.is_required and field.default is None:
                if field.name not in kwargs:
                    raise RequiredAttributeError(field.name)
            elif field.default:
                if field.name not in kwargs:
                    kwargs[field.name] = field.default

        for name, value in kwargs.items():
            field = self._lookup_field(name)
            self._setfield(field, value)

    def __str__(self):
        return str(self._as_dict())

    def _as_dict(self):
        return {
            f.name: self._v[f.name] for f in self._f
            if f.name in self._v
        }

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

    def _lookup_field(self, name):
        field = object.__getattribute__(self, name)
        if not isinstance(field, Field):
            raise AttributeError(name)
        return field

    def _setfield(self, field, value):
        if value is None:
            if field.is_required:
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
            message = str(err)
            if message:
                error += f": {message}"
            raise ValueError(error) from err
        field.after_set(self)

    def __delattr__(self, name):
        field = self._lookup_field(name)
        if field.is_required:
            raise AttributeError("cannot delete a required field")
        del self._v[name]
