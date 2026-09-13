from typing import Protocol, assert_type

from stipulate import CompatibilityResult, Contract


class Storage(Protocol):
    def read(self, key: str) -> bytes: ...


contract = Contract(Storage)
assert_type(contract, Contract[Storage])
assert_type(contract.contract, Contract[Storage])
assert_type(contract.validate(object()), Storage)
assert_type(contract.validate(object(), strict=False), Storage)
assert_type(contract.check(object()), CompatibilityResult)
