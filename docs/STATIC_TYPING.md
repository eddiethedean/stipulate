# Static Typing Strategy

## Goal

Stipulate is **Pyright strict from the beginning and permanently forward**.

A package centered on Python interface contracts should hold itself to a high internal typing standard. Strict typing is therefore a project invariant, not a cleanup phase or pre-release hardening task.

## Required checker mode

The repository must configure Pyright with:

```json
{
  "typeCheckingMode": "strict"
}
```

Equivalent `pyproject.toml` configuration is acceptable if it produces the same behavior.

All first-party source code must pass Pyright strict with zero errors before merge.

## Scope

Strict checking applies to:

- `src/stipulate/`;
- public API modules;
- internal implementation modules;
- CLI code;
- optional integration packages when installed in their supported environments;
- typing fixtures intended to demonstrate valid usage;
- documentation examples that are promoted as type-safe examples.

Tests may use narrowly justified exceptions where test construction requires intentionally invalid typing, but suppressions must be local and documented.

## No warning-debt policy

Do not accumulate typing debt for later cleanup.

New code must not introduce broad suppressions such as file-wide `# pyright: ignore`, blanket `Any`, or disabled strict diagnostics merely to unblock implementation.

When dynamic Python behavior genuinely cannot be represented precisely, isolate it behind a small typed boundary and document the reason.

## Suppression policy

A suppression is acceptable only when all of the following are true:

1. the behavior is intentional;
2. the checker cannot currently express it correctly;
3. the suppression is as narrow as practical;
4. a comment explains the limitation when it is non-obvious;
5. the surrounding public API remains precisely typed.

Typing workarounds for the `Interface` runtime bridge should be centralized rather than repeated across the codebase.

## Desired declaration

```python
from stipulate import Interface


class Repository(Interface):
    def get(self, id: int) -> User | None: ...
```

Ordinary implementations should satisfy it structurally:

```python
class PostgresRepository:
    def get(self, id: int) -> User | None:
        ...


def use(repo: Repository) -> None:
    ...


use(PostgresRepository())
```

## Interface bridge

Python's typing specification treats `Protocol` specially. A normal subclass of a protocol is not automatically structural unless the special Protocol form participates in the declaration.

The prototype therefore uses a typing-facing `Interface` representation compatible with `Protocol` and a runtime representation that injects Stipulate machinery through `__mro_entries__`.

This mechanism must itself be proven under Pyright strict across every supported Python version.

## Method-first API challenge

The desired public API is:

```python
Repository.validate(candidate)
Repository.check(candidate)
Repository.compare(RepositoryV2)
Repository.schema()
Repository.fingerprint()
Repository.contract
```

Current Python typing has a known limitation around simultaneously representing `Interface` as the special Protocol base and exposing Stipulate metaclass methods to the checker.

This is a first-class technical problem. The project should not silently waive strict checking around the public API.

Any accepted solution must either:

- make the method-first API pass Pyright strict directly; or
- provide a narrowly scoped, clearly documented typing representation/stub strategy while preserving the same runtime API.

A free-function fallback may exist only if required by current typing limitations and should remain secondary to the intended API.

## Existing Protocols

```python
from stipulate import Contract

Storage = Contract(StorageProtocol)
```

The `Contract` API must be fully typed under Pyright strict, including return types for `validate()`, `check()`, `compare()`, schema access, and fingerprints.

## Checker matrix

Pyright strict is the primary mandatory checker.

CI must run it on every supported Python/package configuration where feasible.

Mypy remains an important interoperability target and should have conformance fixtures, but passing mypy must not weaken the Pyright strict baseline.

## Public typing guarantees

Public APIs should avoid leaking `Any` unless the underlying typing semantics genuinely require it.

Generic APIs should preserve types precisely. For example, validating against a contract should return the interface/contract type rather than `object` or `Any` wherever Python typing can express that relationship.

## Stub policy

Ship complete type information with the package. If `.pyi` files are required to represent runtime metaclass tricks safely, they are part of the public API and must themselves pass the checker suite.

Never expose private CPython typing implementation classes such as `_ProtocolMeta` in public annotations.

## Strictness and dynamic internals

Runtime introspection inevitably touches dynamic objects. The implementation should convert dynamic/unknown data into normalized typed internal structures as early as practical.

Prefer:

```text
untyped/dynamic Python boundary
        ↓
small normalization layer
        ↓
strictly typed Contract IR and compatibility engine
```

rather than spreading `Any` throughout the engine.

## CI rule

A change that fails Pyright strict is not merge-ready.

Strict typing remains required for all future releases, refactors, integrations, and performance rewrites, including any future Rust/PyO3 boundary on the Python side.
