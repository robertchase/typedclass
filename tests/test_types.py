import decimal
import pytest

from typedclass import Boolean, Decimal


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
