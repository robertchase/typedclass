import pytest

from typedclass import Typed, Field
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
