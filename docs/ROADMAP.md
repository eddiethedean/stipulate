# Roadmap and Release Scope

This document owns delivery scope. DESIGN_DECISIONS.md owns policy; focused documents own behavioral details; OPEN_TECHNICAL_PROBLEMS.md records unfinished implementation evidence. A selected policy is not a passed release gate.

## Status

The repository is a design-stage project with isolated design probes. Prior prototype reports are historical and must be reproduced in versioned tests before being counted as production evidence.

## Authoritative feature matrix

| Capability | 0.1 scope | Later gate |
| --- | --- | --- |
| Declaration | Standard Protocol plus Contract(Protocol) | Interface shorthand: OTP-001/002 |
| Methods | Ordinary instance def and coroutine async def; complete basic call-shape handling | Class/static methods, generators, callable objects: OTP-012/016 |
| Type forms | None, nominal types and typing numeric promotions, Any evidence, unions, Literal, Annotated underlying types | Other forms remain explicit unsupported diagnostics |
| Collections | list, set, dict, fixed/variadic tuple, Sequence, Iterable, Mapping with documented variance/origin relations | General generic specialization: OTP-006/007 |
| Attributes | Declared plain storage and standard read/write properties, without getter execution | Custom/dynamic/generated descriptors: OTP-012/014 |
| Resolution | Trusted/raw policies; common resolvable strings and legacy aliases; explicit namespaces | PEP 695 and recursive aliases: OTP-005 |
| Enforcement | Strict by default; explicit limited permissive acceptance | No silent expansion of the allowlist |
| Results | Three statuses, independent completeness, evidence, stable initial exports | Report schema stability by 1.0 |
| Errors | ContractDefinitionError and ContractError from the start | Semver guarantees by 1.0 |
| Caching | Retained Contract snapshot, weak global keys/values, explicit refresh | Automatic mutation tracking deferred |
| Typing | TypeForm inference, Pyright strict, supported mypy configuration, installed-distribution fixtures | Broader checker versions after tests |
| Developer experience | Plain str/repr reports, actionable diagnostics, complete quickstart | Observed beta usability: OTP-029 |
| Internal IR | Immutable normalized records | Internal shape is not a public schema |
| schema()/fingerprint() | Not public | Phase 5 / OTP-023 |
| compare()/CompatibilityReport | Not public | Phase 6 / OTP-027 |
| Current-value checking | Not in core 0.1 | Separate later opt-in design |
| CLI and snapshots | Not in 0.1 | After schema and comparison gates |
| Pydantic integration | No core dependency | Optional post-1.0 |

No row implies support for other generic origins, overloads, nested Protocol annotations, Self, ParamSpec, TypeVarTuple, Unpack, or typed kwargs. Unsupported requirement definitions fail compilation; unsupported candidates yield non-permissible unknown evidence.

## Phase 0 — Prove the public boundary

Reproduce TypeForm constructor inference, exact return types, structural composition, negative diagnostics, and wheel/sdist behavior in pinned checker environments. Freeze evidence, annotation evaluation, storage, mutation, and failure policies. Establish the CPython matrix before advertising any supported interpreter.

Interface shorthand research may proceed independently; it cannot delay the usable Contract API or weaken its typing guarantees.

## Phase 1 — Minimal usable core / 0.1

Deliver exactly the 0.1 matrix: Contract, compiler/IR, static member discovery with an explicit inspection policy, call-shape and finite type relations, evidence/errors, snapshot reuse, and examples.

Every advertised feature needs positive, negative, unknown/definition-error, relevant checker, and Python-version tests. “Unknown” is a documented limitation, not completed support for that feature.

Delivery within Phase 1 follows complete user tasks: first a narrow but working validation/diagnostic path, then call-shape and type expansion, then supported storage and operational hardening. These internal slices do not change the supported 0.1 matrix or imply partial features are releasable.

Public beta additionally requires the experience exercise in EXPERIENCE_DESIGN.md. Its task-completion targets must be measured on the installed package; passing static probes is insufficient.

## Phase 2 — Ordinary typing and member expansion

Add nested Protocol relations, newer aliases, class/static binding, selected descriptors and decorators, and richer storage handling only with explicit conformance and inspection policies. Distinguish runtime value checking from declaration compatibility.

## Phase 3 — User generics

Specialize TypeVars consistently across all members. Add bounds, constraints, inheritance, explicit/inferred variance, and coherent recursive substitution. Builtin collection support from 0.1 does not count as this phase being complete.

## Phase 4 — Advanced callable forms

Overloads, ParamSpec, Concatenate, Self, TypeVarTuple, Unpack, typed kwargs, generators, and richer awaitable relations each require independent specification-driven gates. They are not mandatory for 1.0 unless advertised.

## Phase 5 — Versioned schema

Specify canonical identity, portability, ignored metadata, defaults, recursion, and schema compatibility. Only then expose schema() and fingerprint(). Do not stabilize an accidental dictionary format through examples.

## Phase 6 — Evolution and CI

Expose compare() with separate implementer/consumer results, three-valued breaking status, and fail-closed CI policy for unknowns. Reuse the engine with explicit universal-guarantee context rather than treating gradual acceptance as proof.

Snapshots and optional Typer/Rich tooling follow stable schema and comparison semantics.

## Phase 7 — 1.0 hardening

Require a stable advertised API/subset, Python and checker matrix, diagnostic/schema compatibility policy, specification corpus, property tests, cache lifecycle/concurrency tests, benchmarks, and mature examples. Unsupported advanced features stay explicitly unsupported; 1.0 does not mean implementing all Python typing.

## Post-1.0

Pydantic value/report integration is optional. Proxies, framework adapters, generated test doubles, and a native core remain possibilities requiring demonstrated need. Integration work must not alter core compatibility results.
