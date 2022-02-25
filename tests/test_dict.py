from typedclass import Typed, Field


class Case1(Typed):
    DEFAULT = "foo"
    a = Field(default=DEFAULT)


def test_as_dict():
    t = Case1()
    assert t.as_dict() == {"a": "foo"}


def test_from_dict():
    t = Case1.from_dict({"a": "bar", "b": "what?"})
    assert t.a == "bar"
    assert not hasattr(t, "b")
