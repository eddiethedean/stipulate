"""Static API-shape evidence only; contract_api is a stub, not a validator."""

from typing import Protocol, assert_type

from contract_api import Contract, CompatibilityResult, CompatibilityStatus, DiagnosticRecord, Evidence


class Readable(Protocol):
    def read(self, key: str) -> bytes: ...


class Writable(Protocol):
    def write(self, key: str, value: bytes) -> None: ...


class Storage(Readable, Writable, Protocol):
    pass


class MemoryStorage:
    def read(self, key: str) -> bytes:
        return key.encode()

    def write(self, key: str, value: bytes) -> None:
        pass


implementation: Storage = MemoryStorage()
storage_contract = Contract(Storage)
assert_type(storage_contract, Contract[Storage])
assert_type(storage_contract.contract, Contract[Storage])
assert_type(storage_contract.validate(object()), Storage)
assert_type(storage_contract.validate(object(), strict=False), Storage)
assert_type(storage_contract.check(object()), CompatibilityResult)
assert_type(storage_contract.check(object()).status, CompatibilityStatus)
assert_type(storage_contract.check(object()).complete, bool)
assert_type(storage_contract.check(object()).accepted(strict=False), bool)
assert_type(Contract(Storage, refresh=True), Contract[Storage])
assert_type(Contract(Storage, annotations="raw"), Contract[Storage])
assert_type(Contract[Storage](Storage), Contract[Storage])

assert_type(storage_contract.check(object()).errors(), list[DiagnosticRecord])
assert_type(storage_contract.check(object()).unknowns(), list[DiagnosticRecord])
assert_type(storage_contract.check(object()).evidence, tuple[Evidence, ...])

assert_type(str(storage_contract.check(object())), str)
assert_type(repr(storage_contract.check(object())), str)
assert_type(repr(storage_contract), str)
