import pytest

from typedclass import Typed, Field, Kwargs
from typedclass import ExtraAttributeError, DuplicateAttributeError
from typedclass import RequiredAttributeError, NoneValueError


class Case1(Typed):
    DEFAULT = "foo"
    a = Field(default=DEFAULT)


@pytest.mark.parametrize("case", (
    (Case1()),
    (Case1(Case1.DEFAULT)),
    (Case1(a=Case1.DEFAULT)),
))
def test_default(case):
    assert case.a == Case1.DEFAULT


def test_non_default():
    t = Case1(value := "bar")
    assert t.a == value  # arg
    t = Case1(a=value)
    assert t.a == value  # kwarg


@pytest.mark.parametrize("args, result", (
    (["foo", "extra"], "extra"),
    (["foo", "extra", "bar"], "extra, bar"),
))
def test_extra(args, result):
    with pytest.raises(ExtraAttributeError) as extra:
        Case1(*args)
    assert extra.value.args[0] == f"extra attribute(s): {result}"


def test_duplicate():
    with pytest.raises(DuplicateAttributeError) as duplicate:
        Case1("foo", a="bar")
    assert duplicate.value.args[0] == "duplicate attribute: a"


def test_invalid():
    with pytest.raises(AttributeError) as invalid:
        Case1(b="yikes")
        assert invalid.args[0] == "b"


class Case2(Typed):
    DEFAULT = "foo"
    a = Field(is_required=True)
    b = Field(is_required=True, default=DEFAULT)


def test_required_missing():
    with pytest.raises(RequiredAttributeError) as required:
        Case2()
    assert required.value.args[0] == "missing required attribute: a"


@pytest.mark.parametrize("kwargs, result", (
    ({"a": None}, "a"),
    ({"a": "bar", "b": None}, "b"),
))
def test_required_none(kwargs, result):
    with pytest.raises(NoneValueError) as required:
        Case2(**kwargs)
    assert required.value.args[0] == f"field cannot be null: {result}"


def test_required_default():
    value = "bar"
    case = Case2(value)
    assert case.a == value
    assert case.b == Case2.DEFAULT


class Case3(Typed):
    a = Field()
    b = Field()
    c = Kwargs()


def test_kwargs():
    case = Case3(a=1, b=2, x=1, y=2, z=3)
    assert case.c == dict(x=1, y=2, z=3)


def test_kwargs_as_dict():
    case = Case3(a=1, b=2, x=1, y=2, z=3)
    assert case.as_dict() == dict(a="1", b="2", c=dict(x=1, y=2, z=3))


class Case4(Typed):
    a = Field(default="A")


class Case5(Case4):
    b = Field()


def test_inherited_field():
    case = Case5(a=1, b=2)
    assert case.as_dict() == dict(a="1", b="2")


class Case6(Case4):
    a = Field(default="AA")


def test_overridden_field():
    case = Case6()
    assert case.a == "AA"


class Case7(Case5):
    c = Field()


def test_three_deep():
    case = Case7(a=1, b=2, c=3)
    assert case.as_dict() == dict(a="1", b="2", c="3")


class Case8(Typed):
    d = Field()


class Case9(Case7, Case8):
    e = Field()


def test_deep_and_wide():
    case = Case9(a=1, b=2, c=3, d=4, e=5)
    assert case.as_dict() == dict(a="1", b="2", c="3", d="4", e="5")


class Case10:
    f = Field()


class Case11(Typed, Case10):
    g = Field()


def test_non_typed_class_with_fields():
    case = Case11(f=1, g=2)
    assert case.as_dict() == dict(f="1", g="2")
