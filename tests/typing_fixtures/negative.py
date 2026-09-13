from typing import Protocol

from stipulate import Contract


class Storage(Protocol):
    def read(self, key: str) -> bytes: ...


contract = Contract(Storage)
wrong_result: int = contract.validate(object())
wrong_contract: Contract[int] = contract
wrong_declaration = Contract[int](Storage)
contract.check(object(), strict=False)
Contract(Storage, strict=False)
