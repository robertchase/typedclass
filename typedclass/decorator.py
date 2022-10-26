from functools import wraps

from typedclass import Typed, Field, Kwargs


def DynamicTyped(**field_kwargs):
    """build a Typed class from a dict of name/Field kwargs"""

    class _Typed(Typed):
        """dynamic typedclass"""
        pass

    for key, val in field_kwargs.items():
        if isinstance(val, Field):
            val.name = key
        elif isinstance(val, Kwargs) and getattr(_Typed, "_k"):
            raise Exception("duplicate Kwargs specified")
        elif isinstance(val, Kwargs):
            setattr(_Typed, "_k", key)
        else:
            raise Exception(f"non-Field argument specified: {key}")
        setattr(_Typed, key, val)

    _Typed._f = [field for field in field_kwargs.values() if isinstance(field, Field)]
    return _Typed


def typedfunction(**field_kwargs):
    """function decorator that enforces argument types

       Wrap a function in type-checking code.  The "field_kwargs" parameters
       list the names and types (using Field instances) of each of the
       function's parameters. By default the values passed to the function are
       not serialized; this can be changed by passing a True to the returned
       decorator before wrapping the function.
    """

    _typed = DynamicTyped(**field_kwargs)

    def serializer(serialize=False):
        def inner(func):
            @wraps(func)
            def _inner(*args, **kwargs):
                normalized = _typed(*args, **kwargs)
                return func(**normalized.as_dict(serialize=serialize))
            return _inner
        if serialize not in (True, False):  # serialize not specified
            func = serialize  # treat serialize as func
            serialize = False
            return inner(func)
        return inner
    return serializer
