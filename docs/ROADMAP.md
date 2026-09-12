# Roadmap

The roadmap defines delivery phases. The authoritative backlog of unresolved correctness and compatibility questions is [OPEN_TECHNICAL_PROBLEMS.md](OPEN_TECHNICAL_PROBLEMS.md). Roadmap work that changes semantics should map to one or more OTP items and satisfy their acceptance criteria before the feature is treated as complete.

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

Primary OTPs: OTP-001, OTP-003, OTP-004, OTP-010, OTP-012, OTP-021.

## Phase 1 — Minimal usable core

Target: first installable package suitable for experimentation.

Deliverables:

- package skeleton and `pyproject.toml`;
- `Interface`;
- `validate()`;
- `InterfaceAdapter`;
- immutable compiled interface model;
- structured `InterfaceValidationError`;
- distinct interface-definition failure handling;
- method and async method validation;
- parameter shape validation;
- basic assignability engine;
- common annotation resolution and forward references;
- properties and attributes;
- inheritance;
- weak-reference compilation cache;
- pytest suite;
- mypy/Pyright fixtures;
- documentation examples;
- explicit Python support matrix.

Gate: no advertised feature without positive, negative, error, checker, and version tests. Every 0.1-blocking OTP must either be resolved or have a deliberately frozen and documented policy.

Primary OTPs: OTP-001, OTP-003, OTP-004, OTP-005, OTP-010, OTP-012, OTP-013, OTP-015, OTP-016, OTP-020, OTP-021, OTP-022, OTP-025.

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
- descriptor semantics;
- better dynamic-member diagnostics;
- class-versus-instance validation policy;
- improved decorator/signature recovery.

Gate: conformance corpus demonstrates intentional parity with the typing spec and documents checker differences.

Primary OTPs: OTP-004, OTP-005, OTP-011, OTP-012, OTP-014, OTP-015, OTP-017.

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

Primary OTPs: OTP-006, OTP-007.

## Phase 4 — Advanced callable typing

Target: complex framework/plugin contracts.

Work:

- overload sets;
- `ParamSpec`;
- `Concatenate`;
- complex `Callable` forms;
- `Self`;
- `TypeVarTuple` and `Unpack` where meaningful;
- typed `**kwargs` patterns;
- richer async/generator semantics where justified.

This phase should be driven by concrete typing-spec fixtures, not ad hoc introspection.

Primary OTPs: OTP-008, OTP-009, OTP-016, OTP-018, OTP-019.

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

Primary OTP: OTP-023. OTP-002 may be revisited if Python typing capabilities improve.

## Phase 6 — 1.0 hardening

Requirements before 1.0:

- explicit Python support matrix;
- stable public API;
- stable error codes;
- schema versioning policy if schema APIs are public;
- comprehensive typing conformance suite;
- performance benchmarks;
- fuzz/property tests for signature normalization;
- no known silent false-positive behavior for supported constructs;
- clear unsupported-type behavior;
- mature docs and migration policy;
- all pre-1.0 OTP items resolved, explicitly deferred, or removed from advertised support.

Primary OTPs: OTP-022, OTP-023, OTP-024, OTP-025, plus any unresolved correctness items from earlier phases.

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
