import pytest

from typedclass import Typed, Field
from typedclass import ExtraAttributeError, DuplicateAttributeError
from typedclass import RequiredAttributeError, NoneValueError


class Case1(Typed):
    DEFAULT = "foo"
    a = Field(default=DEFAULT)


def test_default():
    t = Case1()
    assert t.a == Case1.DEFAULT
    t = Case1(Case1.DEFAULT)


def test_non_default():
    t = Case1(value := "bar")
    assert t.a == value  # arg
    t = Case1(a=value)
    assert t.a == value  # kwarg


def test_extra():
    with pytest.raises(ExtraAttributeError) as extra:
        Case1("foo", "extra")
        assert extra.args[0] == "'extra',"
    with pytest.raises(ExtraAttributeError) as extra:
        Case1("foo", "extra", "bar")
        assert extra.args[0] == "'extra', 'bar',"


def test_duplicate():
    with pytest.raises(DuplicateAttributeError) as duplicate:
        Case1("foo", a="bar")
        assert duplicate.args[0] == "a"


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
        assert required.args[0] == "a"


def test_required_none():
    with pytest.raises(NoneValueError) as required:
        Case2(a=None)
        assert required.args[0] == "a"
    with pytest.raises(NoneValueError) as required:
        Case2(a="bar", b=None)
        assert required.args[0] == "b"


def test_required_default():
    value = "bar"
    case = Case2(value)
    assert case.a == value
    assert case.b == Case2.DEFAULT
