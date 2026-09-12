# Dependency Strategy

## Principle

Stipulate should keep its core dependency surface small. Dependencies may reduce implementation risk and improve user experience, but Stipulate must own its contract IR, assignability semantics, evidence model, and compatibility engine.

## Core candidates

### `typing-extensions`

Preferred core dependency when needed to provide consistent modern typing features across supported Python versions.

### `attrs`

Evaluate before adoption for immutable/slotted internal models such as `Contract`, `Evidence`, and compatibility results. Standard-library dataclasses remain a valid alternative. Do not add `attrs` merely for convenience if it does not materially simplify the implementation.

### `typing-inspection`

Evaluate experimentally for runtime annotation inspection/normalization. Do not make it foundational until its behavior has been tested against Stipulate's typing conformance corpus and support matrix.

## CLI

### Typer

Typer is the preferred CLI framework for Stipulate.

Reasons:

- mature and familiar in the Python ecosystem;
- type-hint-oriented command definitions;
- strong documentation and adoption;
- natural fit for Stipulate's small command vocabulary;
- integrates well with Rich for readable terminal output.

Typer should remain optional so library-only users do not need CLI dependencies.

Proposed packaging:

```text
pip install "stipulate[cli]"
```

Potential CLI surface:

```text
stipulate check
stipulate snapshot
stipulate diff
```

The CLI must consume the same `Contract` and compatibility engine used by the Python API. It must not implement independent compatibility rules.

### Rich

Rich is the preferred companion for human-readable CLI reports if/when the CLI ships.

Use it for semantic compatibility reports, tables, summaries, and CI-friendly terminal output. Keep structured machine-readable output independent from Rich.

## Optional integrations

### Pydantic

Post-1.0 optional integration only. See `PYDANTIC_INTEGRATION.md`.

Suggested extra:

```text
stipulate[pydantic]
```

Pydantic must not become a core dependency or assignability engine.

### Griffe

Do not add as a core dependency. It may be evaluated later if Stipulate gains a concrete need for whole-package/static API extraction that cannot be justified in the explicit-contract core.

## Development and conformance dependencies

### pytest

Primary test runner.

### Hypothesis

Strongly recommended for property-based testing of callable normalization, assignability relations, contract transformations, and evolution invariants.

### mypy and Pyright

Required conformance tools for the public structural-typing experience. Checker fixtures should be part of CI.

### Typeguard / Beartype

Useful as research/reference systems and possibly differential-test inputs for narrow runtime typing cases, but not runtime dependencies or semantic authorities.

## Standard library first

Prefer the standard library for functionality that does not justify another dependency:

- `inspect` for runtime inspection;
- `typing` for standard typing primitives;
- `weakref` and `functools` for initial caching;
- `hashlib` for fingerprints;
- `json` for canonical serialization where sufficient;
- `dataclasses` unless `attrs` demonstrates a material advantage.

## Native/Rust core

Do not add a Rust/native dependency before profiling demonstrates a meaningful need. Design canonical Contract IR so a future PyO3/maturin core remains possible without moving Python introspection into Rust.

## Dependency acceptance rule

A new runtime dependency should satisfy at least one of these conditions:

1. removes a substantial amount of difficult non-differentiating code;
2. materially improves correctness or cross-version compatibility;
3. provides a mature user-facing capability that would be wasteful to rebuild;
4. is optional and unlocks a clearly valuable integration.

Do not add dependencies merely because they provide abstractions similar to code Stipulate can implement simply with the standard library.

## Current preferred posture

```text
Core
  typing-extensions
  attrs?                evaluate
  typing-inspection?    evaluate

CLI extra
  typer
  rich

Post-1.0 integration
  pydantic

Dev / conformance
  pytest
  hypothesis
  mypy
  pyright
```
