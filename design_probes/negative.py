"""Intentionally invalid examples: checker failures are expected, not ignored."""

from typing import Protocol

from contract_api import Contract


class Readable(Protocol):
    def read(self, key: str) -> bytes: ...


class Writable(Protocol):
    def write(self, key: str, value: bytes) -> None: ...


class OrdinarySubclass(Readable, Writable):
    pass


class Storage(Readable, Writable, Protocol):
    pass


class MemoryStorage:
    def read(self, key: str) -> bytes:
        return key.encode()

    def write(self, key: str, value: bytes) -> None:
        pass


class NarrowReader:
    def read(self, key: bytes) -> bytes:
        return key


ordinary: OrdinarySubclass = MemoryStorage()  # expected: nominal-subclass
reader: Readable = NarrowReader()  # expected: incompatible-parameter
Contract[int](Storage)  # expected: mismatched-type-argument
invalid_return: str = Contract(Storage).validate(object())  # expected: return-type
Contract(Storage, annotations="evaluate_safely")  # expected: invalid-policy
