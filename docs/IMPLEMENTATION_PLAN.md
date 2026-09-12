# Implementation Plan

## Objective

Turn the validated prototype into a maintainable production package without losing the typing semantics that make Stipulate valuable.

The authoritative unresolved-engineering backlog is [OPEN_TECHNICAL_PROBLEMS.md](OPEN_TECHNICAL_PROBLEMS.md). Implementation work must map semantic changes to OTP items and satisfy their acceptance criteria before those problems are considered resolved.

## Non-negotiable project invariant: Pyright strict

Stipulate is **Pyright strict from the first implementation commit onward**.

The repository must configure:

```json
{
  "typeCheckingMode": "strict"
}
```

or the equivalent `pyproject.toml` setting.

A change is not merge-ready if first-party code fails Pyright strict.

Do not defer typing cleanup to later milestones. Dynamic runtime behavior must be isolated behind small normalization boundaries rather than allowing `Any` to spread through the contract engine.

Broad ignores, disabled strict diagnostics, or file-wide checker suppressions are not acceptable substitutes for design work. Narrow suppressions are permitted only for genuine checker limitations and must be documented.

## Milestone 1 — Package foundation

Create the package skeleton around the contract engine:

```text
src/stipulate/
    __init__.py
    _interface.py
    _contract.py
    _compile.py
    _members.py
    _signatures.py
    _assignability.py
    _annotations.py
    _compatibility.py
    _evidence.py
    _errors.py
    _cache.py

tests/
typing_tests/
benchmarks/
```

Add:

- `pyproject.toml`;
- Pyright with `typeCheckingMode = "strict"`;
- pytest;
- mypy interoperability fixtures;
- Ruff or equivalent linting;
- coverage;
- CI across supported Python versions;
- Hypothesis for property-based compatibility tests when the first assignability engine lands.

Pyright strict must pass before Milestone 1 is considered complete.

## Milestone 2 — Interface bridge

Implement and freeze the smallest possible runtime bridge supporting:

```python
class Foo(Interface):
    ...
```

Requirements:

- `Foo` is a genuine runtime protocol;
- framework methods do not become protocol members;
- inheritance remains valid;
- ordinary static structural typing works;
- the bridge and its stubs/typing representation pass Pyright strict;
- behavior is regression-tested across every supported Python version.

The desired method-first API must remain an explicit typing design target:

```python
Foo.validate(obj)
Foo.check(obj)
Foo.compare(FooV2)
```

Do not normalize checker errors around these methods with blanket ignores.

## Milestone 3 — Contract IR

Implement the immutable semantic core:

- `Contract`;
- typed contract member records;
- normalized callable/signature model;
- normalized type-expression representation where needed;
- inherited member collection;
- annotation resolution;
- canonical serialization foundation;
- weak-reference compilation cache.

The compiler contains no candidate-specific validation state.

All IR types should be precise enough to keep the compatibility engine free of pervasive `Any`.

## Milestone 4 — Evidence and errors

Implement structured evidence and result models before expanding validation logic:

- `Evidence`;
- `CompatibilityResult`;
- `ContractError`;
- `ContractDefinitionError`.

Distinguish proven, incompatible, and unknown evidence explicitly.

## Milestone 5 — Callable compatibility

Implement call-shape compatibility independently from type assignability:

1. positional-only;
2. positional-or-keyword;
3. keyword-only;
4. defaults;
5. extra required parameters;
6. `*args`;
7. `**kwargs`;
8. binding normalization;
9. async mismatch detection;
10. decorator/signature recovery policy.

Build specification-oriented fixtures before advanced annotations.

## Milestone 6 — Assignability engine

Implement directional assignability explicitly:

```python
is_assignable(source, destination, context=...)
```

Initial cases:

- identity;
- `Any` with deliberate policy;
- missing annotations under strict/permissive evidence rules;
- `None`;
- nominal subclass relationships;
- unions;
- `Literal`;
- `Annotated` underlying type;
- common generic forms with known variance.

Use parameter contravariance and return covariance correctly.

Unsupported constructs produce explicit unknown/unsupported evidence rather than equality fallback.

## Milestone 7 — Attributes and properties

Implement separate semantic representations for readable/writable attributes and properties.

Do not infer declaration compatibility solely from a current runtime value.

Define policy for custom descriptors, dynamic members, and instance-only attributes.

## Milestone 8 — Method-first public API

Implement the intended public experience:

```python
Foo.validate(value)
Foo.check(value)
Foo.compare(FooV2)
Foo.contract
Foo.schema()
Foo.fingerprint()
```

Existing Protocols use:

```python
contract = Contract(MyProtocol)
contract.validate(value)
```

The method-first API is the design target. If Python typing limitations require a stub or narrowly scoped fallback mechanism, solve that explicitly without weakening repository-wide Pyright strict mode.

## Milestone 9 — Checker conformance

Create fixtures executed by Pyright strict and mypy.

Verify:

- structural implementation acceptance;
- statically invalid implementations rejected;
- method-first API typing;
- precise validation return types;
- `Contract(Protocol)` typing;
- interface inheritance;
- generic behavior only when actually supported;
- no accidental public `Any` leakage.

Pyright strict is mandatory. Mypy is an interoperability target, not a reason to weaken strict Pyright design.

## Milestone 10 — Hardening

Before the first public beta:

- Hypothesis/property tests around signature shape and assignability invariants;
- decorator/wrapper tests;
- dynamic attribute tests;
- forward-reference tests;
- multi-evidence aggregation tests;
- cache lifecycle/thread-safety tests;
- mutation/cache policy tests;
- benchmark baseline;
- documentation examples executed and type-checked where practical.

## Later milestones

After the ordinary core is trustworthy:

- generic specialization and variance;
- overloads and advanced callable typing;
- canonical schemas and fingerprints;
- semantic interface evolution;
- snapshot/CI tooling;
- optional CLI via Typer/Rich;
- optional post-1.0 Pydantic integration;
- optional native/Rust core only if benchmarks justify it.

## Implementation rules

### Pyright strict forever

Strict mode is permanent project policy across new modules, refactors, CLI code, optional integrations, and future releases.

### Do not use annotation equality as a fallback

Unsupported typing constructs must remain explicit.

### Do not call candidate methods during structural validation

Validation is introspective unless a future explicitly separate behavioral feature says otherwise.

### Minimize private `typing` coupling

Isolate CPython/runtime Protocol internals behind a small typed compatibility layer.

### Prefer immutable compiled metadata

Contracts should be safe to cache and share.

### Treat open technical problems as release gates

Happy-path code is not enough.

## Definition of done for 0.1

A 0.1 release must demonstrate the core contract experience while the repository passes Pyright strict with zero first-party errors.

It should support ordinary interfaces with correct structural recognition, runtime validation, variance-aware callable checks, async checks, attributes/properties for documented cases, structured evidence/errors, cached compilation, explicit unsupported diagnostics, and supported Python versions proven in CI.

Do not expand the feature set until this base is trustworthy.