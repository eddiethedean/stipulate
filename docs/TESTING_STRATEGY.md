# Testing Strategy

## Objective

Stipulate's correctness depends more on edge-case semantics than on happy-path API coverage. The test suite must therefore be specification-oriented and matrix-driven.

## Test layers

### Unit tests

Cover individual normalization and assignability rules:

- parameter kinds;
- defaults;
- variadics;
- covariance/contravariance;
- unions;
- `Any`;
- `Literal`;
- properties;
- async functions;
- annotation resolution;
- inheritance;
- strict/permissive modes.

### Contract compilation tests

Verify that interface classes compile into stable metadata:

- correct member classification;
- inherited member merging;
- overriding behavior;
- unsupported definitions;
- forward references;
- caching identity.

### Validation integration tests

Exercise complete interfaces against valid and invalid implementations.

Each test should assert both acceptance/rejection and structured error details.

### Static checker fixtures

Maintain source fixtures intended to pass or fail under:

- mypy;
- Pyright.

Fixtures should specifically test:

- `class Foo(Interface):` structural behavior;
- unrelated structural implementations;
- `validate(Foo, obj)` inferred return type;
- `InterfaceAdapter[Foo]` return typing;
- inheritance;
- generics as they become supported;
- known class-side `model_validate` limitation.

### Typing conformance corpus

Build a curated corpus of callable/protocol examples derived from the Python typing specification.

For each case track:

```text
expected by spec
mypy result
Pyright result
Stipulate result
```

Runtime and static results need not always match because available information differs, but every disagreement should have a documented reason.

## Python version matrix

Support should be explicit. Initial implementation should target modern Python versions and run CI across every advertised version.

Do not rely on private `typing` internals remaining stable across Python versions without dedicated regression tests.

The `Interface` runtime bridge is especially important to test across the full supported Python matrix.

## Regression tests

Every discovered bug in assignability, signature handling, annotation resolution, or protocol construction should receive a minimal regression fixture before the fix is merged.

## Error snapshots

Human-readable errors may use snapshot tests, but structured `.errors()` assertions should be the authoritative compatibility checks.

Avoid brittle snapshots that block harmless formatting improvements.

## Property-based testing

Property-based testing is valuable for signature compatibility once the core algorithm stabilizes.

Potential generated dimensions include:

- parameter kind sequences;
- defaults;
- variadic presence;
- simple inheritance graphs;
- union combinations.

Generated signatures must remain valid Python signatures.

## Mutation testing

Consider mutation testing after initial coverage is strong, especially for variance direction and boolean compatibility rules where reversed conditions can pass ordinary coverage unnoticed.

## Performance tests

Benchmark tests should be separate from correctness tests and should not use fragile wall-clock thresholds in normal CI.

Track benchmark history for:

- cold compilation;
- cached validation;
- adapter validation;
- large interfaces.

## Minimum quality gate

Before a feature is advertised as supported it should have:

1. positive runtime tests;
2. negative runtime tests;
3. structured error assertions;
4. checker fixtures where the construct has static meaning;
5. Python-version coverage;
6. documentation.

Unsupported typing constructs should have tests confirming they fail or degrade in the documented way rather than being accidentally accepted.
