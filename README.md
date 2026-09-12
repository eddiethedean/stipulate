# Stipulate

**Enforceable runtime contracts for Python structural interfaces.**

Stipulate lets developers define behavioral contracts with normal Python class syntax, keep those contracts useful to existing static type checkers, and validate dynamic implementations deeply at runtime.

> **Define an interface once. Use it with the type checker you already have. Validate implementations where static typing ends.**

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

The goal is to provide for object interfaces what Pydantic provides for data validation: a declarative model, a compiled validation engine, structured errors, predictable semantics, and strong developer ergonomics.

## Why Stipulate?

Static type checking works when the checker can see the relationship between an implementation and an interface. Real applications also receive objects dynamically through plugins, dependency injection, configuration, entry points, drivers, backends, mocks, and third-party extension APIs.

At that boundary, Stipulate answers a stronger question than shallow runtime Protocol checks:

> **Can this object actually be used safely according to this interface contract?**

Stipulate is built around four promises:

1. **Use the type system you already have.** Interfaces remain structural Python types useful to mypy, Pyright, Pylance, IDEs, and ordinary annotations.
2. **Validate where static typing ends.** Dynamically obtained implementations can be verified before the application depends on them.
3. **Validate compatibility, not appearance.** Callable variance, call shape, async semantics, properties, attributes, and inheritance matter—not merely member names or textual signature equality.
4. **Turn interfaces into tooling artifacts.** Compiled contracts and structured errors establish a foundation for schemas, documentation, plugin tooling, and future interface compatibility analysis.

Implementations remain ordinary Python classes. They should not need to inherit from Stipulate, register themselves, use decorators, or depend on Stipulate.

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

## Where it fits

Stipulate is particularly useful at dynamic boundaries:

```python
plugin = load_plugin(config.plugin)
plugin = validate(Plugin, plugin)
```

```python
backend = container.resolve(Storage)
backend = validate(Storage, backend)
```

```python
fake = TestRepository()
validate(Repository, fake, strict=True)
```

Stipulate is not intended to replace static checking. It complements it when static proof is unavailable.

## Error experience

Contract failures should be precise and machine-readable:

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

Structured errors should be consumable by CI systems, frameworks, IDE tooling, and tests.

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
- **Interface specialization over general runtime typing.** Stipulate should remain focused on complete object contracts rather than becoming another general function-instrumentation library.

## Future contract tooling

Once the assignability engine and compiled interface representation are sufficiently trustworthy, Stipulate can potentially analyze interface evolution:

```python
compare_interfaces(StorageV1, StorageV2)
```

This could identify breaking and non-breaking contract changes for plugin APIs, frameworks, and libraries. A versioned `interface_schema()` can likewise support documentation, visualization, manifests, CI, and generated tooling.

These capabilities depend on correctness of the underlying interface model and should not outrun it.

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
- [Competition Evaluation](docs/COMPETITION.md)
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
