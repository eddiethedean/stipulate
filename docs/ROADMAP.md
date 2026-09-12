# Roadmap

## Phase 0 — Prototype validation

Goal: prove the architecture before committing to public API stability.

Completed/proven in prototype form:

- `class Foo(Interface):` runtime construction;
- genuine runtime protocol identity;
- runtime class-side validation sugar;
- free `validate()` API;
- signature inspection;
- parameter contravariance;
- return covariance;
- positional/keyword compatibility;
- defaults and variadics;
- async mismatch detection;
- properties/attributes;
- inheritance;
- strict/permissive annotation behavior;
- structured errors;
- compiled interface caching.

Remaining prototype validation:

- actual mypy and Pyright CI matrix for the final packaging layout;
- multi-version Python verification of the `Interface` bridge;
- clearer static-vs-runtime attribute semantics.

## Phase 1 — Minimal usable core

Target: first installable package suitable for experimentation.

Deliverables:

- package skeleton and `pyproject.toml`;
- `Interface`;
- `validate()`;
- `InterfaceAdapter`;
- immutable compiled interface model;
- structured `InterfaceValidationError`;
- method and async method validation;
- parameter shape validation;
- basic assignability engine;
- properties and attributes;
- inheritance;
- weak-reference compilation cache;
- pytest suite;
- mypy/Pyright fixtures;
- documentation examples.

Gate: no advertised feature without positive, negative, error, checker, and version tests.

## Phase 2 — Typing correctness expansion

Target: broaden coverage of ordinary modern Python typing.

Work:

- robust unions;
- `Literal`;
- `Annotated`;
- aliases;
- forward references;
- nested protocols as annotations;
- collection variance rules;
- classmethod/staticmethod semantics;
- writable properties;
- better dynamic-member diagnostics;
- improved descriptor safety.

Gate: conformance corpus demonstrates intentional parity with the typing spec and documents checker differences.

## Phase 3 — Generics

Target: correct generic interface specialization.

Work:

- `TypeVar` resolution;
- constrained and bounded variables;
- covariance and contravariance;
- Python 3.12+ inferred variance;
- parameterized interface adapters;
- inherited generic interfaces;
- generic return inference.

Do not ship partial generic semantics that silently erase type parameters.

## Phase 4 — Advanced callable typing

Target: complex framework/plugin contracts.

Work:

- overload sets;
- `ParamSpec`;
- `Concatenate`;
- complex `Callable` forms;
- `Self`;
- `TypeVarTuple` and `Unpack` where meaningful;
- typed `**kwargs` patterns.

This phase should be driven by concrete typing-spec fixtures, not ad hoc introspection.

## Phase 5 — Schema and tooling

Target: make compiled interfaces useful outside direct validation.

Work:

- versioned `interface_schema()` format;
- schema serialization;
- CLI inspection command;
- documentation rendering helpers;
- plugin/framework integration examples;
- optional checker enhancements if there is proven value.

Potential uses:

- plugin registration;
- dependency injection;
- mock/fake verification;
- framework extension APIs;
- generated developer documentation.

## Phase 6 — 1.0 hardening

Requirements before 1.0:

- explicit Python support matrix;
- stable public API;
- stable error codes;
- schema versioning policy;
- comprehensive typing conformance suite;
- performance benchmarks;
- fuzz/property tests for signature normalization;
- no known silent false-positive behavior for supported constructs;
- clear unsupported-type behavior;
- mature docs and migration policy.

## Post-1.0 possibilities

These are intentionally not commitments:

- optional enforcement proxies;
- class-level preflight validation for plugin registration;
- framework adapters;
- richer IDE/checker integration;
- protocol diffing/version compatibility;
- contract compatibility reports between interface versions;
- generated test doubles;
- validation hooks for dependency injection containers.

## Guiding rule

Stipulate should expand by making more Python typing semantics correct, not by accumulating convenience features faster than the validation engine can support them safely.
