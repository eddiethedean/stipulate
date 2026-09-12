# Product Vision

## Summary

Stipulate is a runtime structural interface validation library for Python. Its purpose is to make behavioral contracts feel as natural and trustworthy as Pydantic models while preserving compatibility with the static type-checking ecosystem developers already use.

The conceptual analogy is:

- Pydantic validates **data shape and values**.
- Stipulate validates **object shape, callable contracts, and behavioral interface declarations**.

## Problem

Python already has `typing.Protocol`, but runtime protocol checks are intentionally shallow. A runtime-checkable protocol can establish that members exist, but it does not deeply validate whether method signatures, parameter types, return types, async behavior, properties, or attributes are compatible with the declared contract.

This creates a gap for applications that need to accept plugins, adapters, repositories, service objects, dependency-injected implementations, drivers, strategies, backends, extension points, or user-supplied implementations safely at runtime.

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
- generated documentation and schemas.

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

## Differentiation

Stipulate should not compete by inventing another interface declaration language. The declaration syntax is normal Python typing syntax.

The differentiation is the combination of:

1. native structural typing;
2. deep runtime validation;
3. Pydantic-style error quality;
4. compiled/cached interface metadata;
5. alignment with Python typing assignability rules;
6. no required checker plugin for the core experience.

## Non-goals

Stipulate is not intended to:

- replace Pyright or mypy;
- become a full static type checker;
- replace `typing.Protocol` conceptually;
- validate runtime behavior by executing arbitrary methods;
- proxy every validated object;
- enforce business logic or semantic correctness;
- invent alternative variance or assignability rules;
- silently accept typing constructs it cannot validate correctly.

## Success criteria

A successful 1.0 release should make the following statement credible:

> If an implementation contains enough runtime type information, Stipulate can deeply validate whether it satisfies a Python structural interface and explain any mismatch with precise, structured errors.

The static and runtime stories should reinforce each other rather than contradict each other.
