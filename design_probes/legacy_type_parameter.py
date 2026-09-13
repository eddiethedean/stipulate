"""Pyright accepts this legacy fallback; the recorded mypy rejects it."""

from typing import Protocol, TypeVar, assert_type, cast

T = TypeVar("T")


class Storage(Protocol):
    def read(self, key: str) -> bytes: ...


def legacy_validate(declaration: type[T], candidate: object) -> T:
    # This is only a typing probe. The cast performs NO runtime validation.
    return cast(T, candidate)


validated = legacy_validate(Storage, object())  # expected-mypy: type-abstract
assert_type(validated, Storage)
