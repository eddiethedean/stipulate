# Product Vision

## Summary

Stipulate turns Python structural interfaces into enforceable runtime contracts.

Its purpose is to make behavioral contracts feel as natural and trustworthy as Pydantic models while preserving compatibility with the static type-checking ecosystem developers already use.

The conceptual analogy is:

- Pydantic validates **data shape and values**.
- Stipulate validates **object capabilities and interface compatibility**.

The central product promise is:

> Define an interface once, use it with the type checker you already have, and validate dynamic implementations where static typing ends.

## Problem

Python already has `typing.Protocol`, but runtime protocol checks are intentionally shallow. A runtime-checkable protocol can establish that members exist, but it does not deeply establish whether an implementation can safely be used according to the declared callable and member contracts.

Static checking also has a natural boundary. Pyright or mypy can reason about an implementation when the relationship is statically visible, but applications frequently receive implementations dynamically through:

- plugin discovery;
- entry points and dynamic imports;
- dependency injection;
- configuration;
- framework extension APIs;
- dynamically selected drivers/backends;
- mocks and test doubles;
- third-party or user-supplied implementations.

At those boundaries the application has an object, not a static proof that the object satisfies the expected contract.

Stipulate exists to validate that boundary.

## Product thesis

Developers should be able to write:

```python
from stipulate import Interface


class Storage(Interface):
    name: str

    def read(self, key: str) -> bytes | None: ...
    async def write(self, key: str, value: bytes) -> None: ...
```

and get a contract that is simultaneously useful for:

- editor completion;
- Pyright/Pylance;
- mypy;
- ordinary Python annotations;
- runtime validation;
- framework introspection;
- structured diagnostics;
- generated documentation and schemas;
- future interface compatibility analysis.

Implementations should remain ordinary Python classes and should not need to inherit from Stipulate, register themselves, or depend on Stipulate.

## Why install Stipulate?

Stipulate should earn its dependency through four concrete promises.

### 1. Use the type system developers already have

Stipulate does not require a parallel interface language. Interfaces remain structural Python types that are useful to existing static tooling.

### 2. Validate where static typing ends

Dynamic plugins, injected services, drivers, backends, mocks, and user implementations can be validated at runtime before the application depends on them.

### 3. Validate compatibility, not appearance

The question is not merely whether appropriately named members exist or whether signatures are textually equal.

Stipulate should answer:

> Can every operation permitted by this interface safely be performed against this implementation?

That requires reasoning about call shape, parameter assignability, return assignability, async semantics, member kinds, inheritance, and eventually generic relationships.

### 4. Turn interfaces into tooling artifacts

A compiled interface should become useful beyond a single boolean check. Structured errors, compiled metadata, schemas, and future compatibility analysis can support plugin systems, CI, documentation, testing, framework tooling, and contract evolution.

## Killer boundary: dynamic implementations

Consider a framework loading a storage implementation dynamically:

```python
storage = load_plugin(config.storage_backend)
storage = validate(Storage, storage)
```

A static checker cannot prove the dynamically loaded object satisfies `Storage` at that point. Shallow member-presence checks are not enough if the methods exist but cannot safely accept the interface's legal calls.

This is the primary adoption story for Stipulate.

## Core UX

The primary API should remain small:

```python
class Repository(Interface):
    def get(self, id: int) -> User | None: ...

repo = validate(Repository, candidate)
```

The validated value should be the original object, not a wrapper:

```python
validate(Repository, candidate) is candidate
```

unless a future explicit proxy API is requested.

Existing ordinary `Protocol` declarations should be adoptable through `InterfaceAdapter` without requiring a migration to Stipulate interface declarations.

## Error experience

Failure should explain the contract mismatch precisely rather than return a vague boolean or generic `TypeError`.

Conceptually:

```text
3 validation errors for PaymentProvider

authorize.amount
  Implementation parameter type is too narrow
  expected implementation to accept: Decimal
  implementation accepts: PositiveDecimal
  [type=parameter_type]

refund
  Expected async method
  [type=async_mismatch]

currency
  Required readable attribute is missing
  [type=missing_attribute]
```

Errors should also be available as stable structured records for frameworks, CI systems, IDE tooling, and tests.

## Differentiation

Stipulate should not compete by inventing another interface declaration language or becoming a general runtime type checker.

The differentiation is the combination of:

1. native structural typing;
2. deep runtime interface validation;
3. validation at dynamic boundaries where static proof is unavailable;
4. assignability semantics rather than annotation/signature equality;
5. Pydantic-style error quality and ergonomics;
6. compiled/cached interface metadata;
7. no required checker plugin for the core experience;
8. future contract inspection and compatibility tooling.

A concise positioning statement is:

> **Standard Python structural typing + deep runtime interface assignability + Pydantic-quality validation ergonomics.**

## Interface compatibility as a future capability

A trustworthy assignability engine and compiled interface representation create an opportunity beyond object validation.

Stipulate should eventually be able to analyze contract evolution:

```python
compare_interfaces(StorageV1, StorageV2)
```

and distinguish changes such as:

- compatible optional parameters;
- breaking parameter narrowing;
- incompatible return widening;
- removed members;
- changed async behavior;
- changed property mutability.

This could make Stipulate useful for semantic-versioning checks in plugin and framework APIs.

This capability should be built only after the underlying assignability semantics are sufficiently complete and trustworthy.

## Machine-readable interface model

A future versioned interface schema can make contracts usable by tooling:

```python
Storage.interface_schema()
```

Potential consumers include:

- generated documentation;
- plugin manifests;
- contract visualization;
- CI compatibility reports;
- mock/fake generation;
- framework introspection;
- developer tooling.

The schema should describe the interface contract rather than attempt to imitate JSON Schema where the semantics do not map naturally.

## Target users

Stipulate is particularly useful for:

- library and framework authors;
- plugin ecosystems;
- dependency injection systems;
- service-oriented Python applications;
- data engineering frameworks with pluggable backends;
- driver and adapter systems;
- testing tools that verify mocks/fakes against real contracts;
- applications loading third-party or dynamically selected implementations.

## Non-goals

Stipulate is not intended to:

- replace Pyright or mypy;
- become a full static type checker;
- replace `typing.Protocol` conceptually;
- become a general function instrumentation framework;
- compete with broad runtime type checkers on total annotation count;
- validate runtime behavior by executing arbitrary methods;
- proxy every validated object;
- become a dependency injection or plugin framework itself;
- enforce business logic or semantic correctness;
- invent alternative variance or assignability rules;
- silently accept typing constructs it cannot validate correctly.

## Success criteria

A successful 1.0 release should make the following statement credible:

> If an implementation contains enough runtime type information, Stipulate can deeply validate whether it safely satisfies a Python structural interface and explain any mismatch with precise, structured errors.

The static and runtime stories should reinforce each other rather than contradict each other.

The strongest user-facing explanation should remain simple:

> **Python's type checker verifies structural contracts when it can see them. Stipulate verifies dynamic implementations at runtime.**
