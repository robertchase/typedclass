import pytest

from typedclass import Typed, Field, List, String, Integer
from typedclass.list import ListTooLongError, ListTooShortError
from typedclass.list import ListDuplicateItemError


class Case1(Typed):
    a = Field(List(String))


def test_basic_init():
    c = Case1(a=[1, "two", "three"])
    assert c
    assert len(c.a) == 3
    assert c.as_dict() == {"a": ["1", "two", "three"]}


def test_set():
    c = Case1()
    assert not hasattr(c, "a")
    c.a = [1, 2]
    assert c.a == ["1", "2"]


def test_index():
    c = Case1(a=[1, 2, 3])
    assert c.a.index("2") == 1


def test_slice():
    c = Case1(a=[1, 2, 3, 4, 5])
    assert c.a[0:] == ["1", "2", "3", "4", "5"]
    assert c.a[1:] == ["2", "3", "4", "5"]
    assert c.a[:-2] == ["1", "2", "3"]
    assert c.a[1:-1] == ["2", "3", "4"]


class Case2(Typed):
    a = Field(List(String, min=3))


@pytest.mark.parametrize("items, success", (
    ([], False),
    ([1], False),
    ([1, 2], False),
    ([1, 2, 3], True),
))
def test_min(items, success):
    if success:
        assert Case2(a=items)
    else:
        with pytest.raises(ListTooShortError) as short:
            Case2(a=items)
        assert short.value.args[0].endswith("length must be at least 3")


class Case3(Typed):
    a = Field(List(String, max=3))


@pytest.mark.parametrize("items, success", (
    ([], True),
    ([1], True),
    ([1, 2], True),
    ([1, 2, 3, 4], False),
))
def test_max(items, success):
    if success:
        assert Case3(a=items)
    else:
        with pytest.raises(ListTooLongError) as short:
            Case3(a=items)
        assert short.value.args[0].endswith("length must be no more than 3")


def test_del_basic():
    c = Case1(a=[1, 2, 3])
    del c.a[1]
    assert c.a == ["1", "3"]


def test_del_min():
    c = Case2(a=[1, 2, 3])
    with pytest.raises(ListTooShortError):
        del c.a[1]


def test_del_slice():
    c = Case1(a=[1, 2, 3, 4])
    del c.a[2:]
    assert c.a == ["1", "2"]


def test_del_slice_min():
    c = Case2(a=[1, 2, 3, 4])
    with pytest.raises(ListTooShortError):
        del c.a[2:]


def test_append_basic():
    c = Case1(a=[1, 2])
    c.a.append(3)
    assert c.a == ["1", "2", "3"]


def test_append_max():
    c = Case3(a=[1, 2, 3])
    with pytest.raises(ListTooLongError):
        c.a.append(4)


class MyType(Typed):
    id = Field(Integer, is_required=True)
    name = Field()


class Case4(Typed):
    a = Field(List(MyType))


@pytest.mark.parametrize("items, result", (
    ([MyType(id=100, name="foo")], {"a": [{"id": 100, "name": "foo"}]}),
    ([{"id": 100}], {"a": [{"id": 100}]}),
    ([{"id": 100}, MyType(id=200)], {"a": [{"id": 100}, {"id": 200}]}),
))
def test_typed(items, result):
    c = Case4(a=items)
    assert c.as_dict() == result


def test_typed_append():
    c = Case4(a=[{"id": 100}])
    c.a.append({"id": 200, "name": "bar"})
    assert c.as_dict() == {"a": [{"id": 100}, {"id": 200, "name": "bar"}]}
    del c.a[1]
    c.a.append(MyType(id=300))
    assert c.as_dict() == {"a": [{"id": 100}, {"id": 300}]}


def test_typed_setattr():
    c = Case4(a=[{"id": 100}, {"id": 200}])
    c.a[1] = {"id": 300, "name": "whatever"}
    assert c.as_dict() == {"a": [{"id": 100}, {"id": 300, "name": "whatever"}]}
    c.a[1] = MyType(id=400)
    assert c.as_dict() == {"a": [{"id": 100}, {"id": 400}]}


class Case5(Typed):
    a = Field(List(Integer, allow_dups=False))


@pytest.mark.parametrize("init, append, is_valid", (
    ([1, 2, 3], 4, True),
    ([1, 2, 3, 3], 4, False),
    ([1, 2, 3], 3, False),
    ([], 1, True),
))
def test_typed_set(init, append, is_valid):

    def run():
        c = Case5(init)
        c.a.append(append)

    if is_valid:
        run()
    else:
        with pytest.raises(ListDuplicateItemError):
            run()


@pytest.mark.parametrize("init, key, value, is_valid", (
    ([1, 2, 3], 1, 4, True),
    ([1, 2, 3], 1, 2, True),
    ([1, 2, 3], 0, 1, True),
    ([1, 2, 3], 0, 2, False),
))
def test_typed_set_setattr(init, key, value, is_valid):
    c = Case5(init)
    if is_valid:
        c.a[key] = value
    else:
        with pytest.raises(ListDuplicateItemError):
            c.a[key] = value
