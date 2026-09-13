# Stipulate

**Contracts for Python interfaces.**

**Define. Validate. Evolve.**

Stipulate checks dynamically supplied implementations against Python structural interfaces, explains mismatches, and preserves what available metadata cannot establish.

## Status

This repository contains the design specification and small design probes. It does not yet contain an installable Stipulate implementation. The examples below describe the planned 0.1 API. Earlier prototypes are historical inputs, not evidence that release gates have passed.

## Define and validate

```python
from typing import Protocol
from stipulate import Contract


class Storage(Protocol):
    def read(self, key: str) -> bytes | None: ...

    async def write(self, key: str, value: bytes) -> None: ...


class MemoryStorage:
    def __init__(self) -> None:
        self._items: dict[str, bytes] = {}

    def read(self, key: str) -> bytes | None:
        return self._items.get(key)

    async def write(self, key: str, value: bytes) -> None:
        self._items[key] = value


candidate = MemoryStorage()
storage_contract = Contract(Storage)
storage = storage_contract.validate(candidate)
```

Implementations are ordinary Python classes. They need no inheritance, registration, or decorators. Validation returns the original object, typed as `Storage`, after checking its available declarations against the contract. The constructor uses TypeForm for inference; the [typing guide](docs/STATIC_TYPING.md) records supported checker settings, including the current mypy feature flag.

Strict validation is the default: incompatible or insufficient evidence raises `ContractError`. To allow missing implementation type annotations deliberately, use `strict=False`; known mismatches and unsupported or uninspectable candidate capabilities still fail. Invalid requirements fail contract construction.

## Understand a result

```python
result = storage_contract.check(candidate)
print(result)

if result:
    print("Storage declarations are compatible")

result.status
result.complete
result.errors()
result.unknowns()
result.evidence
```

`check()` reports candidate mismatches without raising `ContractError`. Truthiness means compatibility was established for every requirement; unknown evidence is false. Invalid contract definitions raise `ContractDefinitionError`. The result includes locations, reasons, and suggested fixes.

Stipulate compares signatures, annotation assignability, binding, and supported member capabilities. It assumes implementations honor their declarations; it does not execute methods to verify their behavior, validate future return values, or prevent later mutation. Annotation resolution may execute Python annotation expressions in the default trusted mode.

## Friendly errors

```text
2 contract errors for Storage

read.key
  Parameter is too narrow: the contract permits str, but the implementation accepts bytes.
  Accept str (or a compatible broader type).
  [parameter_type]

write
  A coroutine method is required, but the implementation is synchronous.
  [async_mismatch]
```

## Interface shorthand — experimental design target

```python
from stipulate import Interface

class Storage(Interface):
    def read(self, key: str) -> bytes | None: ...

storage = Storage.validate(candidate)
```

This shorthand is not a 0.1 promise. It must preserve structural typing, precise class-side methods, inheritance, and clean protocol members in installed-package Pyright/mypy tests before promotion. The supported 0.1 plan uses `Protocol` plus `Contract`, with the same method-based operations and compatibility engine.

## Evolution and tooling — later releases

```python
report = Contract(StorageV1).compare(Contract(StorageV2))
schema = storage_contract.schema()
fingerprint = storage_contract.fingerprint()
```

Comparison will report implementer and consumer compatibility separately. Unknown results cannot certify a non-breaking change. Schemas and fingerprints will be versioned before publication. None of these three operations is in the 0.1 public surface.

## Documentation

Start with the [quickstart](docs/QUICKSTART.md). The [experience design](docs/EXPERIENCE_DESIGN.md) specifies the API journey, readable reports, and usability bar.

- [Product Vision](docs/PRODUCT_VISION.md)
- [Public Interface Model](docs/INTERFACE_MODEL.md)
- [Contract Engine](docs/CONTRACT_ENGINE.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Type System](docs/TYPE_SYSTEM.md)
- [Validation Engine](docs/VALIDATION_ENGINE.md)
- [Static Typing](docs/STATIC_TYPING.md)
- [Errors](docs/ERROR_MODEL.md)
- [Performance and Caching](docs/PERFORMANCE.md)
- [Testing](docs/TESTING_STRATEGY.md)
- [Compatibility](docs/COMPATIBILITY.md)
- [Dependencies](docs/DEPENDENCIES.md)
- [Competition](docs/COMPETITION.md)
- [Pydantic Integration](docs/PYDANTIC_INTEGRATION.md)
- [Roadmap and 0.x release phases](docs/ROADMAP.md)
- [Release and PyPI trusted publishing](docs/RELEASING.md)
- [Design Decisions](docs/DESIGN_DECISIONS.md)
- [Implementation Plan](docs/IMPLEMENTATION_PLAN.md)
- [Open Technical Problems](docs/OPEN_TECHNICAL_PROBLEMS.md)
- [Design probes](design_probes/README.md)

The roadmap owns release scope; design decisions own durable policy; focused specifications own behavior; the open-problem register owns implementation evidence and unresolved acceptance work. Contradictions must be reconciled in the same change. A decision does not count as a tested implementation.
