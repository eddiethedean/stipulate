# Public Interface Model

## Goal

Stipulate should feel like normal Python classes with useful methods, not a collection of helper functions or a custom DSL.

The public vocabulary is:

> **Define. Validate. Evolve.**

## Defining a contract

```python
from stipulate import Interface


class Repository(Interface):
    name: str

    def get(self, id: int) -> User | None: ...

    async def save(self, user: User) -> None: ...

    @property
    def ready(self) -> bool: ...
```

Implementations remain ordinary Python classes and do not inherit from the interface.

## Primary method API

An `Interface` subclass is an active contract object. The primary public API is method-first:

```python
Repository.validate(candidate)
Repository.check(candidate)
Repository.compare(RepositoryV2)
Repository.schema()
Repository.fingerprint()
Repository.contract
```

Documentation should prefer these forms over free functions that take an interface as their first argument.

### Validate

```python
repo = Repository.validate(candidate)
repo = Repository.validate(candidate, strict=True)
```

Successful validation returns the original object. Failure raises `ContractError`.

### Check

```python
result = Repository.check(candidate)
```

`check()` is non-throwing and returns `CompatibilityResult`.

```python
if result:
    register(candidate)

result.compatible
result.complete
result.errors()
result.unknowns()
result.evidence
```

Truthiness represents compatibility, not completeness. Unknown evidence remains available through the result.

### Compare

```python
report = RepositoryV1.compare(RepositoryV2)
```

The report exposes semantic evolution information:

```python
report.breaking
report.implementers
report.consumers
report.changes
```

The exact report API remains subject to evolution-design acceptance tests, but the method form is the intended user experience.

### Contract metadata

```python
Repository.contract
```

is a cached immutable `Contract` representation.

Metadata is exposed as a property because it is state/representation rather than an action.

Operations remain methods:

```python
Repository.schema()
Repository.fingerprint()
```

These may delegate to `Repository.contract.schema()` and `.fingerprint()`.

## Existing Protocols

Zero-migration adoption uses `Contract` directly:

```python
from typing import Protocol
from stipulate import Contract


class RepositoryProtocol(Protocol):
    def get(self, id: int) -> User | None: ...


Repository = Contract(RepositoryProtocol)

Repository.validate(candidate)
Repository.check(candidate)
Repository.compare(other)
Repository.schema()
Repository.fingerprint()
```

`Contract` replaces the previously planned `InterfaceAdapter`/`ContractAdapter` public concepts.

For a `Contract` instance:

```python
Repository.contract is Repository
```

should be the conceptual invariant.

## Public classes

The core public types are intended to be:

```python
Interface
Contract
CompatibilityResult
CompatibilityReport
Evidence
ContractError
ContractDefinitionError
```

Most users should initially need to import only `Interface`, or `Contract` when adapting an existing Protocol.

## Errors

Candidate incompatibility uses:

```python
ContractError
```

Invalid/unresolvable contract definitions use:

```python
ContractDefinitionError
```

`ContractError.errors()` exposes structured findings/evidence suitable for tests and tooling.

## Schema

Use:

```python
Repository.schema()
```

not `interface_schema()`.

The schema represents a Stipulate contract and is not JSON Schema.

Future deserialization may support:

```python
Contract.from_schema(schema)
```

only after schema versioning and type identity semantics are stable.

## Testing ergonomics

A future testing convenience should prefer a method:

```python
Repository.assert_valid(fake_repository)
```

rather than a pytest-specific marker or `assert_contract(Repository, fake)` helper.

The core validation API should already be usable directly in tests, so this helper is not a 0.1 requirement.

## Pythonic behavior

`CompatibilityResult` should support truth testing:

```python
if Repository.check(candidate):
    ...
```

Rich result/report objects should have useful `str`/`repr` output for REPL, notebook, test, and CI usage.

Avoid clever operators such as:

```python
candidate in Repository
Repository[candidate]
Repository @ candidate
Repository(candidate)
```

They obscure validation semantics or imply construction/coercion.

Normal inheritance remains the interface-composition mechanism:

```python
class Storage(Readable, Writable):
    pass
```

## Free functions

Free functions such as:

```python
validate(Repository, candidate)
check(Repository, candidate)
compare(RepositoryV1, RepositoryV2)
compile_contract(Repository)
```

must not be the primary documented interface.

They may exist internally, as thin implementation primitives, or as narrowly justified compatibility APIs where static typing requires them. If a free-function form is retained because current type checkers cannot describe a class-side method correctly, documentation must clearly distinguish that technical fallback from the preferred ergonomic API.

## Static typing caveat

The desired `class Foo(Interface):` syntax and class-side methods create a known limitation in today's typing model: presenting `Interface` to checkers as the special Protocol base does not automatically make Stipulate metaclass methods statically visible.

This is an unresolved technical problem, not a reason to design an inferior user interface prematurely.

The project should target the method-first API while continuing to test possible checker-safe representations. If a statically authoritative fallback is required, keep it minimal and secondary.

## Structural semantics

Stipulate interfaces are structural. Implementations satisfy contracts based on compatible members, not inheritance or registration.

Extra implementation members are allowed by default.

## Member categories

The contract compiler explicitly models:

- instance methods;
- async methods;
- attributes;
- read-only and writable properties;
- class methods;
- static methods;
- inherited members.

Each category must use its actual assignability semantics rather than textual signature equality.

## Interface inheritance

```python
class Readable(Interface):
    def read(self, key: str) -> bytes: ...


class Writable(Interface):
    def write(self, key: str, value: bytes) -> None: ...


class Storage(Readable, Writable):
    pass
```

The compiler merges inherited requirements, applies overriding semantics, and reports impossible/conflicting definitions as contract-definition errors.

## Public API design rule

When an operation naturally belongs to an `Interface` or `Contract`, prefer a method.

Use free functions only when the operation has no natural owner or a documented Python typing limitation requires a fallback.

This keeps the user model centered on the contract itself:

```text
Define
    class Foo(Interface)

Validate
    Foo.validate(obj)
    Foo.check(obj)

Evolve
    Foo.compare(FooV2)

Inspect
    Foo.contract
    Foo.schema()
    Foo.fingerprint()
```
