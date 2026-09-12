# Stipulate

**Contracts for Python interfaces.**

**Define. Validate. Evolve.**

Stipulate turns Python structural interfaces into contracts you can use with existing type checkers, validate at runtime, and compare as they evolve.

```python
from stipulate import Interface


class Repository(Interface):
    def get(self, id: int) -> str | None: ...

    async def save(self, id: int, value: str) -> None: ...


repo = Repository.validate(candidate)
```

Implementations remain ordinary Python classes. They do not need to inherit from Stipulate, register themselves, or use decorators.

## Define

```python
class Storage(Interface):
    def read(self, key: str) -> bytes | None: ...
```

Interfaces remain useful to Python's structural typing ecosystem and are designed to work with existing type checkers.

## Validate

Enforce the contract:

```python
storage = Storage.validate(candidate)
```

Or inspect compatibility without raising:

```python
result = Storage.check(candidate)

if result:
    register(candidate)

result.errors()
result.unknowns()
result.evidence
```

Stipulate checks more than member presence: call shape, parameter and return assignability, async behavior, properties, attributes, and inheritance all contribute to compatibility.

Validation returns the original object when successful.

## Evolve

```python
report = StorageV1.compare(StorageV2)
```

The same compatibility engine used for runtime validation is designed to analyze interface evolution, including separate effects on implementers and consumers.

```python
report.breaking
report.implementers
report.consumers
report.changes
```

## Contract metadata

Every Stipulate interface exposes its compiled contract:

```python
Storage.contract
Storage.schema()
Storage.fingerprint()
```

Schemas, fingerprints, snapshots, and future CI tooling all derive from the same contract representation.

## Existing Protocols

Existing Python `Protocol` declarations can opt in without rewriting implementations:

```python
from typing import Protocol
from stipulate import Contract


class StorageProtocol(Protocol):
    def read(self, key: str) -> bytes | None: ...


Storage = Contract(StorageProtocol)

Storage.validate(candidate)
Storage.check(candidate)
Storage.compare(other)
```

This is the zero-migration adoption path for existing typed codebases.

## Example failure

```text
2 contract errors for Repository

get.id
  Implementation parameter type is too narrow
  expected implementation to accept: int
  implementation accepts: PositiveInt
  [type=parameter_type]

save
  Expected async method
  [type=async_mismatch]
```

Failures raise `ContractError`. Invalid or unresolvable contract definitions use `ContractDefinitionError`.

## Public model

The intended API stays centered on the contract itself:

```python
Storage.validate(obj)
Storage.check(obj)
Storage.compare(StorageV2)
Storage.contract
Storage.schema()
Storage.fingerprint()
```

Advanced users can work with `Contract` directly. Free functions may exist internally or as narrowly justified typing fallbacks, but they are not the primary user interface.

## What Stipulate is not

Stipulate is not a static type checker, general function instrumentation system, dependency injection framework, behavioral pre/postcondition library, or replacement for Python's typing specification.

Its focus is structural interface contracts.

## Documentation

- [Product Vision](docs/PRODUCT_VISION.md)
- [Contract Engine](docs/CONTRACT_ENGINE.md)
- [Public Interface Model](docs/INTERFACE_MODEL.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Type System and Assignability](docs/TYPE_SYSTEM.md)
- [Validation Engine](docs/VALIDATION_ENGINE.md)
- [Static Typing Strategy](docs/STATIC_TYPING.md)
- [Error Model](docs/ERROR_MODEL.md)
- [Performance and Caching](docs/PERFORMANCE.md)
- [Testing Strategy](docs/TESTING_STRATEGY.md)
- [Compatibility Policy](docs/COMPATIBILITY.md)
- [Competition Evaluation](docs/COMPETITION.md)
- [Open Technical Problems](docs/OPEN_TECHNICAL_PROBLEMS.md)
- [Roadmap](docs/ROADMAP.md)
- [Design Decisions](docs/DESIGN_DECISIONS.md)
- [Implementation Plan](docs/IMPLEMENTATION_PLAN.md)

The [Open Technical Problems](docs/OPEN_TECHNICAL_PROBLEMS.md) register is the authoritative backlog for unresolved correctness and compatibility questions.

## Status

Stipulate is in design/prototype stage. The prototype has exercised the `class Foo(Interface):` model, variance-aware runtime validation, structured compatibility evidence, contract serialization/fingerprints, and directional interface comparison.
