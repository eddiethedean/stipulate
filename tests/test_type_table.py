from __future__ import annotations

import types
from collections.abc import Iterable, Mapping, Sequence
from typing import Annotated, Any, Callable, ClassVar, Final, Literal, Protocol, TypeVar

import pytest

from stipulate._evidence import EvidenceStatus as S
from stipulate._relations import relate, supported


@pytest.mark.parametrize(
    ("source", "destination"),
    [
        (bool, int),
        (bool, float),
        (int, float),
        (int, complex),
        (float, complex),
        (None, type(None)),
        (str, object),
        (int | str, object),
        (int, int | str),
        (Literal[True], int),
        (Literal[1, 2], Literal[1, 2, 3]),
        (Literal["x"], str),
        (Annotated[int, object()], float),
        (list[int], list[int]),
        (list[int], Sequence[float]),
        (list[int], Iterable[object]),
        (set[int], Iterable[float]),
        (dict[str, int], Mapping[str, float]),
        (dict[str, int], Iterable[str]),
        (Mapping[str, int], Mapping[str, float]),
        (Mapping[str, int], Iterable[str]),
        (Sequence[int], Iterable[float]),
        (tuple[int, str], tuple[float, object]),
        (tuple[int, int], tuple[float, ...]),
        (tuple[int, ...], Sequence[float]),
        (tuple[()], tuple[()]),
        (tuple[()], Iterable[int]),
        (str, Sequence[str]),
        (bytes, Iterable[int]),
        (bytearray, Sequence[int]),
        (list[int], list),
        (dict[str, int], Mapping),
        (Any, object),
    ],
)
def test_conclusive_type_routes(source: object, destination: object) -> None:
    assert relate(source, destination).status is S.PROVEN


@pytest.mark.parametrize(
    ("source", "destination"),
    [
        (int | str, int),
        (str, int | bytes),
        (object, str),
        (float, int),
        (Literal[True], Literal[1]),
        (int, Literal[1]),
        (list[int], list[float]),
        (set[int], set[float]),
        (dict[str, int], dict[str, float]),
        (dict[int, str], Mapping[float, str]),
        (Mapping[int, str], Mapping[float, str]),
        (tuple[int, ...], tuple[int]),
        (tuple[int], tuple[int, int]),
        (Sequence[int], list[int]),
        (set[int], Sequence[int]),
    ],
)
def test_disproven_type_routes(source: object, destination: object) -> None:
    assert relate(source, destination).status is S.INCOMPATIBLE


@pytest.mark.parametrize(
    ("source", "destination"),
    [
        (Any, int),
        (int, Any),
        (list, list[int]),
        (list[Any], list[int]),
        (Any | int, int),
        (int, Any | str),
    ],
)
def test_gradual_type_routes(source: object, destination: object) -> None:
    result = relate(source, destination)
    assert result.status is S.UNKNOWN and result.code == "gradual_type"


class Nested(Protocol):
    def f(self) -> int: ...


V = TypeVar("V")


@pytest.mark.parametrize(
    "value",
    [
        Callable[[int], str],
        ClassVar[int],
        Final[int],
        V,
        Nested,
        list[Nested],
        types.GenericAlias(dict, (int,)),
        types.GenericAlias(list, (int, str)),
    ],
)
def test_unsupported_forms_precede_shortcuts(value: object) -> None:
    assert not supported(value)
    for destination in (value, object, Any):
        result = relate(value, destination)
        assert result.status is S.UNKNOWN and result.code == "unsupported_type"


def test_nominal_relation_does_not_execute_subclass_hooks() -> None:
    from abc import ABCMeta

    calls: list[str] = []

    class Target(metaclass=ABCMeta):
        @classmethod
        def __subclasshook__(cls, other: type[object]) -> bool:
            calls.append("hook")
            return True

    assert relate(int, Target).status is S.INCOMPATIBLE
    assert calls == []


def test_literal_supportedness_uses_class_identity_without_repr() -> None:
    class EqualityMeta(type):
        def __eq__(cls, other: object) -> bool:
            raise AssertionError("class equality must not run")

        __hash__ = type.__hash__

    class Payload(metaclass=EqualityMeta):
        def __repr__(self) -> str:
            raise AssertionError("payload repr must not run")

    value = Literal[Payload()]
    assert not supported(value)
    assert relate(value, object).status is S.UNKNOWN


def test_nominal_container_subclass_does_not_invent_generic_substitution() -> None:
    class Child(list[int]):
        pass

    assert relate(Child, Sequence).status is S.PROVEN
    result = relate(Child, Sequence[int])
    assert result.status is S.UNKNOWN and result.code == "unsupported_type"


def test_bare_user_generic_is_unsupported_on_each_runtime() -> None:
    import sys

    namespace: dict[str, object] = {}
    source = (
        "class Box[T]: pass"
        if sys.version_info >= (3, 12)
        else "from typing import Generic, TypeVar\nT=TypeVar('T')\nclass Box(Generic[T]): pass"
    )
    exec(source, namespace)
    assert not supported(namespace["Box"])
    assert relate(namespace["Box"], object).code == "unsupported_type"
