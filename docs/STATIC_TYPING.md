# Static Typing Strategy

## Goal

Stipulate must preserve the value of the Python typing ecosystem rather than requiring users to choose between runtime validation and static structural typing.

The desired declaration is:

```python
from stipulate import Interface


class Repository(Interface):
    def get(self, id: int) -> User | None: ...
```

and ordinary implementations should satisfy it structurally:

```python
class PostgresRepository:
    def get(self, id: int) -> User | None:
        ...


def use(repo: Repository) -> None:
    ...


use(PostgresRepository())
```

## Constraint in Python's typing model

Python's typing specification treats `Protocol` specially. A normal subclass of a protocol is not automatically a structural protocol unless the special `Protocol` base participates in the declaration.

This means a simple implementation such as:

```python
class Interface(Protocol):
    ...

class Repository(Interface):
    ...
```

is insufficient for our typing goal.

## Chosen bridge

The prototype uses two representations of `Interface`:

- a typing-facing representation that behaves as `Protocol`;
- a runtime representation that expands the base list through `__mro_entries__` to include both Stipulate runtime machinery and `Protocol`.

Conceptually:

```python
if TYPE_CHECKING:
    Interface = Protocol
else:
    Interface = _InterfaceSentinel()
```

At runtime, the sentinel expands:

```python
class Foo(Interface):
    ...
```

into the effective equivalent of:

```python
class Foo(_RuntimeInterface, Protocol):
    ...
```

This preserves the desired user syntax and genuine runtime protocol identity.

## Class-side API limitation

Stipulate wants Pydantic-style sugar:

```python
Repository.model_validate(candidate)
```

The correct runtime home for that method is the metaclass, because placing it on the protocol itself would make it part of the structural implementation contract.

Current Python typing cannot fully describe, through the single `Interface` alias, both of these facts simultaneously:

1. subclasses are special structural protocols;
2. their class objects expose Stipulate's custom metaclass API.

Therefore:

```python
validate(Repository, candidate)
```

is the statically authoritative API, while:

```python
Repository.model_validate(candidate)
```

may exist as runtime sugar.

Stipulate must document this honestly rather than requiring users to suppress checker errors silently.

## No required checker plugin

The normal experience must not require a mypy or Pyright plugin.

A future optional plugin may improve:

- recognition of class-side sugar;
- richer diagnostics;
- IDE navigation;
- schema inspection;
- Stipulate-specific configuration validation.

But a plugin must never be required for basic structural compatibility.

## Checker matrix

CI should test at least:

- latest supported mypy;
- latest supported Pyright;
- representative Python versions.

Typing fixtures should contain both expected-success and expected-failure examples.

## Public typing guarantees

For the core API, Stipulate should guarantee:

```python
repo = validate(Repository, candidate)
```

is inferred as `Repository`.

Similarly:

```python
adapter = InterfaceAdapter(Repository)
repo = adapter.validate_python(candidate)
```

should preserve the interface type parameter.

## Stub policy

Ship complete type information with the package. If `.pyi` files are needed to represent runtime tricks safely, they are part of the public API contract and must be tested in CI.

Never expose private CPython typing implementation types such as `_ProtocolMeta` in public annotations.

## Checker disagreement

If mypy and Pyright disagree on a valid typing pattern, prefer the most specification-aligned portable form and document unavoidable discrepancies.

Do not introduce implementation hacks solely to satisfy one checker if they undermine runtime correctness or the other checker.
