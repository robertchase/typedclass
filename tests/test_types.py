from datetime import date
import decimal
import pytest

from typedclass import Boolean, Decimal, ISODate, Set, String


@pytest.mark.parametrize("value, result", (
    (True, True),
    (False, False),
    (1, True),
    (0, False),
    ("1", True),
    ("0", False),
))
def test_boolean(value, result):
    assert result == Boolean()(None, value)


def test_bad_boolean():
    with pytest.raises(ValueError):
        Boolean()(None, "eek")


@pytest.mark.parametrize("precision, value, result", (
    (2, 12.34, decimal.Decimal("12.34")),
    (2, "12.34", decimal.Decimal("12.34")),
    (2, "12.344", decimal.Decimal("12.34")),
    (2, "12.346", decimal.Decimal("12.35")),
    (4, "12.34", decimal.Decimal("12.3400")),
))
def test_decimal(precision, value, result):
    assert result == Decimal(precision)(None, value)


def test_bad_precision():
    with pytest.raises(ValueError):
        Decimal("bad")(None, 1)


def test_bad_decimal():
    type = Decimal(2)
    with pytest.raises(ValueError):
        type(None, "bad")


@pytest.mark.parametrize("value, result", (
    ("2020-02-03", date(2020, 2, 3)),
    (date(2020, 2, 3), date(2020, 2, 3)),
))
def test_isodate(value, result):
    assert result == ISODate()(None, value)


@pytest.mark.parametrize("value", (
    ("bad"),
    (100),
    (None),
))
def test_bad_isodate(value):
    with pytest.raises(ValueError):
        ISODate()(None, value)


@pytest.mark.parametrize("valid, value, result", (
    (["A", "B", "C"], "A", "A"),
    (["A", "B", "C"], "B", "B"),
    ([0, None], 0, 0),
    ([0, None], None, None),
))
def test_set(valid, value, result):
    assert result == Set(*valid)(None, value)


@pytest.mark.parametrize("valid, value", (
    (["A", "B", "C"], "D"),
    (["A", "B", "C"], 0),
    (["A", "B", "C"], None),
    ([], "A"),
))
def test_bad_set(valid, value):
    with pytest.raises(ValueError):
        ISODate()(None, value)


@pytest.mark.parametrize("min, max, value, result", (
    (0, None, "test", "test"),
    (1, 10, "test", "test"),
))
def test_string(min, max, value, result):
    assert result == String(min, max)(None, value)


def test_bad_max_string():
    with pytest.raises(AttributeError):
        String(max=-10)


@pytest.mark.parametrize("min, max, value", (
    (3, None, "A"),
    (3, 5, "ABCDEF"),
))
def test_bad_string(min, max, value):
    with pytest.raises(ValueError):
        String(min, max)(None, value)
