# Quickstart

This guide describes the implemented 0.1 API. Install the local project with `python -m pip install .` or use a built wheel. The tested runtime targets are CPython 3.11–3.14; other implementations and future versions are not implied support.

## Define a capability

Use a normal Python Protocol. Implementations remain ordinary classes:

```python
from typing import Protocol
from stipulate import Contract


class Reader(Protocol):
    def read(self, key: str) -> bytes: ...


class MemoryReader:
    def read(self, key: str) -> bytes:
        return key.encode()


reader_contract = Contract(Reader)
candidate = MemoryReader()
reader = reader_contract.validate(candidate)
assert reader is candidate
```

The inferred type of reader is Reader. No inheritance, implementation decorator, or registration is needed. The [typing guide](STATIC_TYPING.md) records the tested TypeForm-compatible checker versions and the mypy feature flag used by installed consumers.

## Understand a mismatch

Continue the example with an implementation that declares a different input type:

```python
class BinaryReader:
    def read(self, key: bytes) -> bytes:
        return key


result = reader_contract.check(BinaryReader())
print(result)
```

The report identifies the required and provided directions:

```text
Incompatible with Reader
1 incompatible findings; 0 unknown findings (0 blocked obligations).

read.key
  The implementation input is too narrow for required caller values
  Required: str
  Provided: bytes
  [parameter_type; incompatible]
```

check() returns a result for candidate mismatches. validate() raises ContractError when the same candidate fails its policy. Report rendering uses existing metadata and does not call read().

## Make uncertainty explicit

An implementation can have an inspectable call shape and still lack type evidence. With no established mismatch, check() reports UNKNOWN, and bool(result) is False. Strict validation rejects that uncertainty by default.

Prefer adding accurate implementation annotations. When you deliberately accept missing or gradual type information, call validate(candidate, strict=False). This option does not waive known mismatches, unavailable signatures, unsupported types, or dynamic member uncertainty. It also does not change an UNKNOWN result into COMPATIBLE.

Use result.errors() for incompatible findings, result.unknowns() for missing evidence, and result.evidence for the full explanation. result.accepted(strict=False) answers the explicit policy question without changing any findings.

## Know the guarantee

A complete compatible result establishes supported declaration compatibility, assuming implementations honor their annotations and exposed signatures. It does not test method bodies, check future return values, or prevent later mutation. Trusted annotation resolution may evaluate Python annotation expressions.

Retain the Contract for repeated checking. If its requirement declaration changes, explicitly create a refreshed snapshot. See the [API model](INTERFACE_MODEL.md), [supported subset](ROADMAP.md), and [annotation policy](VALIDATION_ENGINE.md).
