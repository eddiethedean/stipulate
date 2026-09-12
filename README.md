# Stipulate

**Runtime structural interface validation for Python, designed to feel like Pydantic.**

Stipulate lets developers define behavioral contracts with normal Python class syntax, keep those contracts useful to existing static type checkers, and validate implementations deeply at runtime.

```python
from stipulate import Interface, validate


class Repository(Interface):
    def get(self, id: int) -> str | None: ...

    async def save(self, id: int, value: str) -> None: ...


class PostgresRepository:
    def get(self, id: int) -> str | None:
        return str(id)

    async def save(self, id: int, value: str) -> None:
        ...


repo = validate(Repository, PostgresRepository())
```

The goal is to provide for object interfaces what Pydantic provides for JSON-shaped data: a declarative model, a compiled validation engine, structured errors, predictable semantics, and strong developer ergonomics.

## Core promise

Define an interface once and use it in three places:

1. **Static structural typing** with existing Python tooling.
2. **Runtime contract validation** with deeper checks than `@runtime_checkable`.
3. **Machine-readable interface metadata** for frameworks, plugin systems, dependency injection, testing, documentation, and tooling.

Stipulate should not require a custom mypy or Pyright plugin for ordinary structural typing.

## Intended API

```python
from stipulate import Interface, validate


class Handler(Interface):
    def handle(self, value: str) -> bytes: ...


handler = validate(Handler, candidate)
```

Runtime class-side sugar may also be provided:

```python
handler = Handler.model_validate(candidate)
```

Because current Python typing cannot fully express the class-side metaclass API while also treating `Interface` as the special `Protocol` base through a single alias, `validate(Handler, candidate)` is the statically authoritative API. `Handler.model_validate(...)` is runtime convenience unless typing support improves.

## Why Stipulate exists

Python's `typing.Protocol` is excellent for static structural typing, but its runtime support intentionally checks only shallow member presence. It does not deeply validate callable signatures, parameter compatibility, return types, async behavior, properties, or current attribute values.

Stipulate fills that gap while composing with Python's typing system instead of replacing it.

## Design principles

- **Python typing first.** Follow the typing specification rather than inventing a parallel type system.
- **Structural, not nominal.** Implementations should not need to inherit from interfaces.
- **No checker plugin required for the core experience.**
- **Pydantic-quality errors and ergonomics.**
- **Compatibility, not annotation equality.** Callable variance and assignability matter.
- **Compile once, validate many.** Interface inspection and annotation resolution should be cached.
- **Explicit strictness.** Missing annotations may be accepted in permissive mode and rejected in strict mode.
- **No proxies by default.** Successful validation returns the original object.
- **Runtime truth without pretending to implement unsupported typing features.** Unsupported constructs must fail clearly or be documented as unsupported.

## Documentation

- [Product Vision](docs/PRODUCT_VISION.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Interface Model](docs/INTERFACE_MODEL.md)
- [Type System and Assignability](docs/TYPE_SYSTEM.md)
- [Validation Engine](docs/VALIDATION_ENGINE.md)
- [Static Typing Strategy](docs/STATIC_TYPING.md)
- [Error Model](docs/ERROR_MODEL.md)
- [Performance and Caching](docs/PERFORMANCE.md)
- [Testing Strategy](docs/TESTING_STRATEGY.md)
- [Compatibility Policy](docs/COMPATIBILITY.md)
- [Open Technical Problems](docs/OPEN_TECHNICAL_PROBLEMS.md)
- [Roadmap](docs/ROADMAP.md)
- [Design Decisions](docs/DESIGN_DECISIONS.md)
- [Implementation Plan](docs/IMPLEMENTATION_PLAN.md)

The [Open Technical Problems](docs/OPEN_TECHNICAL_PROBLEMS.md) register is the authoritative backlog for unresolved correctness and compatibility questions. New implementation work that changes Stipulate's semantics should either resolve an existing OTP item or add one before the behavior is treated as designed.

## Initial scope

The first production milestone should support:

- methods;
- async methods;
- positional-only, positional-or-keyword, and keyword-only parameters;
- defaults;
- `*args` and `**kwargs`;
- parameter contravariance;
- return covariance;
- attributes;
- properties;
- interface inheritance;
- `Any`, unions, `Literal`, `None`, normal class inheritance, and common parameterized containers;
- strict and permissive annotation modes;
- structured validation errors;
- cached compiled interfaces.

Advanced generic substitution, overload sets, `ParamSpec`, `TypeVarTuple`, `Self`, complex variance inference, and other advanced typing constructs are later milestones and must not be approximated unsafely.

## Status

Stipulate is in design/prototype stage. The current architecture has been exercised in a prototype, including the `class Foo(Interface):` runtime model and a first implementation of callable compatibility validation.
