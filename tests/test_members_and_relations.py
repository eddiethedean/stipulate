from __future__ import annotations

from typing import Protocol

from stipulate import CompatibilityStatus, Contract


class Shape(Protocol):
    def run(self, value: int, /, *, verbose: bool = False) -> str: ...


class ShapeGood:
    def run(self, value: int, /, *, verbose: bool = False) -> str:
        return str(value)


class ShapeNarrow:
    def run(self, value: int, /) -> str:
        return str(value)


def test_positional_and_keyword_shape() -> None:
    contract = Contract(Shape)
    assert contract.check(ShapeGood()).status is CompatibilityStatus.COMPATIBLE
    result = contract.check(ShapeNarrow())
    assert result.status is CompatibilityStatus.INCOMPATIBLE
    assert result.errors()[0]["type"] == "signature"


class AsyncContract(Protocol):
    async def fetch(self, key: str) -> bytes: ...


class AsyncGood:
    async def fetch(self, key: str) -> bytes:
        return key.encode()


class SyncWrong:
    def fetch(self, key: str) -> bytes:
        return key.encode()


def test_coroutine_kind_is_checked() -> None:
    assert Contract(AsyncContract).check(AsyncGood()).status is CompatibilityStatus.COMPATIBLE
    result = Contract(AsyncContract).check(SyncWrong())
    assert result.status is CompatibilityStatus.INCOMPATIBLE
    assert result.errors()[0]["type"] == "async_mismatch"


class HasValue(Protocol):
    value: int


class Value:
    value: int

    def __init__(self) -> None:
        self.value = 1


class ValueOnlyAnnotation:
    value: int


def test_attribute_presence_is_separate_from_annotation() -> None:
    assert Contract(HasValue).check(Value()).status is CompatibilityStatus.COMPATIBLE
    assert (
        Contract(HasValue).check(ValueOnlyAnnotation()).status is CompatibilityStatus.INCOMPATIBLE
    )


class ReadOnly(Protocol):
    @property
    def value(self) -> int: ...


class ReadOnlyImpl:
    @property
    def value(self) -> int:
        return 1


def test_property_getter_is_not_called_by_inspection() -> None:
    calls = 0

    class Counted:
        @property
        def value(self) -> int:
            nonlocal calls
            calls += 1
            return 1

    result = Contract(ReadOnly).check(Counted())
    assert result.status is CompatibilityStatus.COMPATIBLE
    assert calls == 0
