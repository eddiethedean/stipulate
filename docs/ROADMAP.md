# Roadmap

The roadmap defines delivery phases. The authoritative backlog of unresolved correctness and compatibility questions is [OPEN_TECHNICAL_PROBLEMS.md](OPEN_TECHNICAL_PROBLEMS.md). Roadmap work that changes semantics should map to one or more OTP items and satisfy their acceptance criteria before the feature is treated as complete.

## Phase 0 — Prototype validation

Goal: prove the architecture before committing to public API stability.

Completed/proven in prototype form include the `class Foo(Interface):` bridge, signature inspection, parameter contravariance, return covariance, call-shape checks, async mismatch detection, attributes/properties, inheritance, strict/permissive evidence behavior, structured findings, contract serialization/fingerprints, and directional comparison experiments.

Remaining prototype validation includes the final mypy/Pyright packaging matrix, multi-version Python verification, and clearer static-vs-runtime attribute semantics.

## Phase 1 — Minimal usable core

Target: first installable package suitable for dynamic-boundary validation.

Primary experience:

```python
plugin = PluginInterface.validate(load_plugin(...))
result = PluginInterface.check(plugin)
```

Deliverables include `Interface`, `Contract`, method-first validation/checking, immutable contract IR, structured `ContractError`, definition-error handling, callable/member validation, annotation resolution, inheritance, caching, tests, checker fixtures, examples, and an explicit Python support matrix.

Gate: no advertised feature without positive, negative, error, checker, and version tests.

## Phase 2 — Typing correctness expansion

Broaden support for ordinary modern Python typing: unions, `Literal`, `Annotated`, aliases, forward references, nested protocols, collection variance, class/static methods, writable properties, descriptors, dynamic members, class-versus-instance policy, and decorator/signature recovery.

Gate: conformance corpus demonstrates intentional parity with the typing specification and documents checker differences.

## Phase 3 — Generics

Implement correct generic specialization: `TypeVar` resolution, bounds/constraints, variance, inferred variance where applicable, inherited generics, and generic return relationships.

Do not silently erase unsupported generic semantics.

## Phase 4 — Advanced callable typing

Add overload sets, `ParamSpec`, `Concatenate`, complex `Callable`, `Self`, `TypeVarTuple`, `Unpack`, typed `**kwargs`, and richer async/generator semantics where justified by the typing specification and runtime evidence.

## Phase 5 — Contract schema and tooling

Stabilize a versioned Stipulate contract schema and build serialization, fingerprints, snapshots, CLI inspection, documentation helpers, and plugin/framework examples on top of the canonical contract IR.

## Phase 6 — Interface evolution

Expose semantic evolution through the method-first API:

```python
report = ApiV1.compare(ApiV2)
```

Distinguish implementer and consumer compatibility using the same assignability engine as runtime validation. Add semantic change reports and, once trustworthy, snapshot/CI compatibility checks.

Do not build a second independent diff algorithm.

## Phase 7 — 1.0 hardening

Before 1.0 require a stable public API, explicit Python matrix, stable error-code policy, schema versioning policy where public, comprehensive typing conformance tests, performance benchmarks, property/fuzz tests, clear unsupported-type behavior, and mature documentation/migration policy.

## Post-1.0 integration track — Pydantic

Pydantic integration is intentionally **optional and post-1.0**. See [PYDANTIC_INTEGRATION.md](PYDANTIC_INTEGRATION.md).

Core principle:

> Stipulate owns structural contracts. Pydantic may enhance value validation and serialization where those concerns naturally intersect.

Potential work:

- first-class examples using Pydantic models in Stipulate interface signatures;
- optional current attribute/property value validation through Pydantic `TypeAdapter`;
- optional Pydantic representations/export helpers for compatibility results, evidence, reports, and schema data;
- FastAPI examples where Pydantic validates request/response data and Stipulate validates dynamically loaded or injected service implementations;
- optional tooling models for consuming Stipulate reports as application data.

Packaging should use an optional extra such as:

```text
stipulate[pydantic]
```

Pydantic must not become a core dependency, change Stipulate compatibility semantics, or become the callable/interface assignability engine.

## Other post-1.0 possibilities

These are intentionally not commitments:

- optional enforcement proxies;
- class-level preflight validation for plugin registration;
- framework adapters;
- richer IDE/checker integration;
- generated test doubles;
- validation hooks for dependency injection containers;
- capability-set tooling;
- optional optimized/Rust core if profiling demonstrates a meaningful need.

## Guiding rule

Stipulate should expand by making Python contract semantics more correct and extracting tooling value from the same trustworthy contract model. Integrations should sit on top of that core rather than reshape it.