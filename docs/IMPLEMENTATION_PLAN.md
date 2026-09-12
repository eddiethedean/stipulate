# Implementation Plan

## Objective

Turn the validated prototype into a maintainable production package without losing the typing semantics that make Stipulate valuable.

## Milestone 1 — Package foundation

Create the package skeleton:

```text
stipulate/
    __init__.py
    _interface.py
    _compile.py
    _members.py
    _signatures.py
    _assignability.py
    _annotations.py
    _errors.py
    _cache.py
    adapter.py
    config.py

tests/
typing_tests/
benchmarks/
```

Add:

- `pyproject.toml`;
- pytest;
- mypy test dependency;
- Pyright test dependency/tooling;
- Ruff or equivalent linting;
- coverage;
- CI across supported Python versions.

## Milestone 2 — Interface bridge

Implement and freeze the smallest possible runtime bridge that supports:

```python
class Foo(Interface):
    ...
```

Requirements:

- `Foo` is a genuine runtime protocol;
- Stipulate framework methods do not become protocol members;
- interface inheritance remains valid;
- normal static structural typing works under mypy and Pyright;
- behavior is regression-tested across every supported Python version.

This milestone is a release blocker because the rest of the public API depends on it.

## Milestone 3 — Compiled model

Implement:

- `CompiledInterface`;
- compiled member record types;
- inherited member collection;
- method/property/attribute classification;
- signature normalization;
- annotation resolution;
- weak-reference cache.

The compiler should contain no candidate-specific state.

## Milestone 4 — Error foundation

Implement `InterfaceValidationError` and structured records before expanding validation logic.

Stable initial error codes should be used throughout tests from this point onward.

## Milestone 5 — Callable validation

Implement call-shape compatibility independently from type assignability.

Order:

1. positional-only;
2. positional-or-keyword;
3. keyword-only;
4. defaults;
5. extra required parameters;
6. `*args`;
7. `**kwargs`;
8. method binding normalization;
9. async mismatch detection.

Build specification-oriented fixtures before adding advanced annotations.

## Milestone 6 — Core assignability

Implement a dedicated assignability engine with explicit direction:

```python
is_assignable(source, destination, context=...)
```

Avoid ambiguous helpers named simply `compatible()`.

Initial cases:

- identity;
- `Any`;
- `None`;
- normal subclass relationships;
- unions;
- `Literal`;
- `Annotated` underlying type;
- common generic forms with known variance.

Use this engine contravariantly for callable parameters and covariantly for returns.

## Milestone 7 — Attributes and properties

Implement separate representations for:

- readable attributes;
- writable attributes;
- read-only properties;
- writable properties.

Do not infer full declaration compatibility solely from the current runtime value.

## Milestone 8 — Public APIs

Implement:

```python
validate(interface, value, *, strict=False)
InterfaceAdapter(interface, ...)
InterfaceValidationError
```

Then add runtime convenience APIs:

```python
Foo.model_validate(value)
Foo.interface_schema()
```

Document the class-side typing limitation clearly.

## Milestone 9 — Checker conformance

Create source fixtures executed by both mypy and Pyright.

Must verify:

- structural implementation acceptance;
- invalid implementation rejection where statically knowable;
- inferred return type from `validate()`;
- adapter typing;
- interface inheritance;
- generic behavior only when actually supported.

Record intentional checker disagreements.

## Milestone 10 — Hardening

Before the first public beta:

- fuzz/property tests around signature shape;
- decorator/wrapper tests;
- dynamic attribute tests;
- forward-reference tests;
- multi-error aggregation tests;
- weak-cache lifecycle tests;
- thread-safety tests;
- benchmark baseline;
- documentation examples executed as tests where practical.

## Implementation rules

### Do not use annotation equality as a fallback

If a typing construct is unsupported, return an unsupported diagnostic rather than pretending equality implements assignability.

### Do not call candidate methods during validation

Validation is structural/introspective.

### Keep internals typed

Stipulate itself should run under strict static type checking. A package about interface typing should model high typing quality internally.

### Minimize private `typing` coupling

Isolate compatibility code that interacts with CPython-specific runtime protocol behavior.

### Prefer immutable compiled metadata

Compiled contracts should be safe to share between threads and validation calls.

## Definition of done for 0.1

A 0.1 release should be able to demonstrate:

```python
class Repository(Interface):
    def get(self, id: int) -> User | None: ...
    async def save(self, user: User) -> None: ...
```

with:

- unrelated structural implementations recognized by mypy and Pyright;
- valid implementations accepted at runtime;
- bad parameter variance rejected;
- bad return variance rejected;
- bad signature shape rejected;
- async mismatch rejected;
- properties/attributes validated for the documented scope;
- useful aggregated errors;
- warm validation using cached compilation;
- explicit diagnostics for unsupported constructs.

Do not expand the public feature set until this base is trustworthy.
