# Stipulate

**Contracts for Python interfaces.**

**Define. Validate. Evolve.**

Stipulate turns Python structural interfaces into contracts you can use with existing type checkers, validate at runtime, and compare as they evolve.

```python
from stipulate import Interface, validate


class Repository(Interface):
    def get(self, id: int) -> str | None: ...

    async def save(self, id: int, value: str) -> None: ...


repo = validate(Repository, candidate)
```

Implementations remain ordinary Python classes. They do not need to inherit from Stipulate, register themselves, or use decorators.

## Why Stipulate?

Static typing works when the checker can see an implementation. Real applications also load plugins, inject services, select backends from configuration, and accept third-party implementations dynamically.

Stipulate validates those boundaries using the same structural contracts developers already use for typing.

It is built around three capabilities:

### Define

```python
class Storage(Interface):
    def read(self, key: str) -> bytes | None: ...
```

Interfaces remain useful to mypy, Pyright, Pylance, IDEs, and ordinary Python annotations.

### Validate

```python
storage = validate(Storage, candidate)
```

Stipulate checks interface compatibility beyond member presence, including call shape, parameter and return assignability, async behavior, properties, attributes, and inheritance.

Validation returns the original object when successful.

### Evolve

```python
report = compare_interfaces(StorageV1, StorageV2)
```

Stipulate's contract engine is designed to analyze interface evolution using the same compatibility rules as runtime validation. This enables directional implementer/consumer compatibility, semantic change reports, and future CI contract checks.

## Contract engine

Stipulate's core model is intentionally small:

```text
compile   Python interface → Contract
inspect   Contract + object → CompatibilityResult
validate  enforce a compatibility result
compare   Contract + Contract → compatibility report
serialize Contract → schema / fingerprint / snapshot
```

A compatibility result can preserve what Stipulate proved, disproved, or could not determine from available runtime information. Strict validation can reject unknown evidence without pretending that missing annotations were proven incompatible.

## Example failure

```text
2 validation errors for Repository

get.id
  Implementation parameter type is too narrow
  expected implementation to accept: int
  implementation accepts: PositiveInt
  [type=parameter_type]

save
  Expected async method
  [type=async_mismatch]
```

Errors are structured so frameworks, CI, tests, and developer tools can consume the same evidence.

## Existing Protocols

Stipulate is designed to work with Python's structural typing ecosystem rather than replace it. Existing `Protocol` declarations should be usable through the contract adapter/compiler without rewriting implementations.

## What Stipulate is not

Stipulate is not a static type checker, general function instrumentation system, dependency injection framework, behavioral pre/postcondition library, or replacement for Python's typing specification.

Its focus is structural interface contracts.

## Documentation

- [Product Vision](docs/PRODUCT_VISION.md)
- [Contract Engine](docs/CONTRACT_ENGINE.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Interface Model](docs/INTERFACE_MODEL.md)
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

Stipulate is in design/prototype stage. The current prototype has exercised the `class Foo(Interface):` model, variance-aware runtime validation, structured compatibility evidence, contract serialization/fingerprints, and directional interface comparison.
