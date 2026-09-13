# Open Technical Problems

This register is authoritative for unfinished acceptance work. ROADMAP.md owns release scope, DESIGN_DECISIONS.md owns policy, and focused specifications own behavior. Cross-references below describe coupled work, not a topological build order; IMPLEMENTATION_PLAN.md orders delivery.

The original register is preserved in [the historical archive](history/OPEN_TECHNICAL_PROBLEMS_ORIGINAL.md). Earlier prototype labels are not release evidence. No OTP is marked resolved merely because this reconciliation selected a policy.

Statuses distinguish open implementation work, deferred scope, and isolated design-probe evidence. “Resolved” requires checked-in acceptance tests passing against the actual implementation and its supported version matrix.

## OTP-001 — Interface bridge portability

**Status:** Open; historical prototype report not reproduced

**Release target:** Experimental; not a 0.1 blocker

### Problem

The desired class Foo(Interface) bridge must preserve real Protocol behavior while remaining isolated from private typing internals.

### Selected policy

Use standard Protocol plus Contract for 0.1. Bridge experiments must not become a prerequisite for the supported API.

### Acceptance tests

- Run the same runtime member-discovery and construction fixtures across the advertised CPython matrix.
- Check single/multiple inheritance and explicit Protocol-marker extension in both supported checkers.
- Confirm implementations require no Stipulate inheritance and framework helpers never enter the required member set.
- Test installed wheel/sdist behavior and isolate any private typing coupling.

### Related work

OTP-002, OTP-010, OTP-025

## OTP-002 — Typed Interface class-side methods

**Status:** Open; promotion gated

**Release target:** Experimental; not a 0.1 blocker

### Problem

A Protocol re-export does not by itself make Foo.validate() visible to checkers; a normal helper base can pollute structural members.

### Selected policy

The intended shorthand remains a target. Do not ship user-facing ignores, Any returns, checker plugins, or generated per-interface stubs as its solution. Contract(TypeForm[T]) is the supported path, not a type[T] free-function fallback.

### Acceptance tests

- Both checkers infer exact Foo return types for Foo.validate() while accepting unrelated valid implementations.
- Invalid structural implementations and invalid validation uses are rejected.
- Class-side helpers remain absent from the runtime protocol member set.
- Composition, packaging, and runtime behavior satisfy OTP-001.

### Related work

OTP-001, OTP-026

## OTP-003 — Callable call-shape containment

**Status:** Open; historical prototype report not reproduced

**Release target:** 0.1 blocker

### Problem

Candidate methods must accept every legal interface call, not just sampled calls or textually matching signatures.

### Selected policy

Use deterministic normalized shape containment with binding handled exactly once.

### Acceptance tests

- Cover positional-only, positional-or-keyword, keyword-only, keyword names, defaults, variadics, and additional required parameters.
- Include collisions between keyword names and positional/variadic binding.
- Property tests use valid signatures and bounded call oracles.
- Unavailable signatures produce non-permissible unknown evidence.

### Related work

OTP-004, OTP-015

## OTP-004 — Finite runtime type relations

**Status:** Open; historical prototype report not reproduced

**Release target:** 0.1 blocker for the roadmap subset

### Problem

Runtime metadata must support directional type relations without equality fallback or loss of gradual uncertainty.

### Selected policy

TYPE_SYSTEM.md and ROADMAP.md define the initial finite forms and origin table. Type relations are metadata conclusions, assuming declarations are honored.

### Acceptance tests

- Test parameter contravariance, return covariance, read/write relations, unions, literals, numeric promotions, and supported collection substitutions.
- Distinct Literal value types and unsupported identical forms do not pass incorrect fast paths.
- Missing and Any-dependent evidence follow OTP-028; unsupported origins remain unknown or definition errors.
- Record specification sections and intentional checker disagreements.

### Related work

OTP-010, OTP-028

## OTP-005 — Annotation resolution and evaluation policy

**Status:** Open; policy selected

**Release target:** 0.1 blocker for common cases

### Problem

String, deferred, imported, local, and recursive annotations cannot always be resolved from available namespaces. Evaluation can execute Python code.

### Selected policy

Trusted evaluation is the default and may execute annotation expressions. Raw mode does not request evaluation. Unresolved requirements fail definition compilation; candidate-only failures remain non-permissible unknown evidence. Neither mode is a sandbox.

### Acceptance tests

- Cover eager/future/deferred annotations across supported versions and use harmless side-effect counters.
- Test raw mode without evaluating annotation factories or deferred functions.
- Test cross-module refs, TYPE_CHECKING-only imports, explicit local namespaces, and unresolved names.
- Custom namespaces bypass global caching; no arbitrary import is attempted for resolution.
- Recursive unsupported forms terminate with clear diagnostics.

### Related work

OTP-013, OTP-021, OTP-025

## OTP-006 — Generic interface specialization

**Status:** Open

**Release target:** Phase 3; not general 0.1 support

### Problem

User TypeVars must be bound coherently across members and substituted through nested and inherited types.

### Selected policy

Builtin collection-origin rules do not imply support for arbitrary generic interfaces. Do not erase unsupported type arguments.

### Acceptance tests

- Cover repeated TypeVars, bounds/constraints, multiple variables, inherited bindings, and inconsistent substitutions.
- Specify specialized versus unspecialized behavior before advertisement.
- Prevent recursive substitution from looping or binding the same variable inconsistently.

### Related work

OTP-004, OTP-007

## OTP-007 — General generic variance

**Status:** Open

**Release target:** Phase 3

### Problem

User generics can be invariant, covariant, contravariant, or use inferred variance; runtime metadata may be incomplete.

### Selected policy

The 0.1 supported collection table is finite. General variance remains a separate gate.

### Acceptance tests

- Test explicit and inferred variance against specification fixtures.
- Cover inherited generic origin substitutions, producer/consumer examples, and mutable invariance.
- Unknown variance is unsupported rather than guessed.

### Related work

OTP-004, OTP-006

## OTP-008 — Overload-set relations

**Status:** Open

**Release target:** Phase 4; required only if advertised

### Problem

Every required overload must be supported with its input/output correlations despite incomplete runtime overload metadata.

### Selected policy

Do not reduce an overload set to unrelated unions or trust a broad runtime signature to establish each correlated return.

### Acceptance tests

- Test disjoint/overlapping overloads, broad implementations, missing coverage, and return correlations.
- Specify metadata precedence and behavior for .pyi-only overloads.
- Missing metadata yields explicit uncertainty or definition diagnostics.

### Related work

OTP-003, OTP-004, OTP-015

## OTP-009 — Advanced callable packs

**Status:** Deferred

**Release target:** Phase 4

### Problem

ParamSpec, Concatenate, TypeVarTuple, and Unpack require explicit parameter-pack representations.

### Selected policy

Do not flatten packs into arbitrary args/kwargs or infer support from successful imports.

### Acceptance tests

- Each construct gets specification-based substitution, binding, and negative fixtures.
- Unsupported packs fail explicitly in requirements and remain non-permissible unknowns in candidates.

### Related work

OTP-003, OTP-004, OTP-006

## OTP-010 — Checker conformance and disagreements

**Status:** Open

**Release target:** 0.1 blocker for public API and supported forms

### Problem

Checker acceptance, runtime evidence, and language semantics differ; all must be recorded accurately.

### Selected policy

Use the typing specification first, explicit runtime policy second, and checker accommodations only without silent semantic changes. Pyright strict is permanent.

### Acceptance tests

- Pin supported checker versions and feature flags.
- Run valid and intentionally invalid installed-distribution fixtures with exact inferred types and expected diagnostic codes.
- Record the type[T] Protocol-value disagreement and required explicit Protocol composition.
- Expand the relation corpus alongside OTP-004 rather than making their mutual references an impossible scheduling cycle.

### Related work

OTP-026; OTP-004 for the expanding relation corpus

## OTP-011 — Instance storage versus class preflight

**Status:** Open; policy selected

**Release target:** 0.1 instance semantics; class preflight deferred

### Problem

Class annotations do not establish storage created by __init__; classes used as objects have different binding semantics from instances.

### Selected policy

Target instance validation in 0.1. Do not infer constructed instance conformance from an implementation class. Reject unsupported class-object candidates explicitly; a future class-preflight API has separate guarantees.

### Acceptance tests

- Test present/missing initialized storage, class attributes, annotations-only members, and slots.
- Only claim presence that supported static inspection establishes.
- Reject unsupported class-object validation without instantiation or misleading success.

### Related work

OTP-012, OTP-014

## OTP-012 — Attributes, properties, and descriptor capabilities

**Status:** Open; policy selected

**Release target:** 0.1 documented plain storage/properties; Phase 2 expansion

### Problem

Read/write declarations and current values are different obligations. Descriptors can hide or execute behavior.

### Selected policy

Core 0.1 uses declared read/write types plus supported presence checks. Standard properties are inspected without calling them. Custom/generated descriptors and cached_property remain explicit limitations.

### Acceptance tests

- Test read covariance, write contravariance, writable invariance, and rejection of read-only properties for writable contracts.
- Test a matching current value with an incompatible declared writable type.
- Getter/setter/dynamic hook counters remain untouched.
- Unsupported storage and custom dispatch yield explicit uncertainty.

### Related work

OTP-004, OTP-011, OTP-014

## OTP-013 — Definition and candidate failures

**Status:** Open; policy selected

**Release target:** 0.1 blocker

### Problem

An invalid requirement must not be reported as a candidate mismatch or silently tolerated by permissive validation.

### Selected policy

ContractDefinitionError and ContractError exist from 0.1. Eager construction validates requirements independently of strictness.

### Acceptance tests

- Test unresolved/unsupported requirements, malformed declarations, and conflicting inherited members.
- Test ordinary candidate incompatibility, missing evidence, and strict unknown rejection.
- check() never raises ContractError for an expected candidate outcome but preserves definition/internal failures.
- Do not cache exception objects or tracebacks.

### Related work

OTP-005, OTP-022, OTP-028

## OTP-014 — Dynamic members and inspection uncertainty

**Status:** Open; policy selected

**Release target:** 0.1 explicit limitation; expanded in Phase 2

### Problem

__getattr__, custom __getattribute__, proxies, custom binding, and extension objects may not expose trustworthy static capabilities.

### Selected policy

Do not invoke dynamic hooks to seek compatible evidence in either strict or permissive core validation. Preserve explicit non-permissible unknowns.

### Acceptance tests

- Test dynamic attributes/callables, proxies, unavailable builtin signatures, and overridden dispatch.
- Distinguish ordinary missing members from uninspectable dynamic members.
- Verify no access hook is called merely to improve evidence.

### Related work

OTP-003, OTP-012, OTP-028

## OTP-015 — Decorator signature recovery

**Status:** Open; policy selected

**Release target:** 0.1 blocker

### Problem

__signature__, __wrapped__, and the visible wrapper can provide different declarations.

### Selected policy

Prefer a valid exposed __signature__, then the supported wrapped chain, then the visible signature. Trust exposed metadata without claiming to prove wrapper behavior.

### Acceptance tests

- Test explicit overrides, wraps, intentional public signature changes, stacked wrappers, cycles, and malformed metadata.
- Normalize binding once and preserve the selected provenance.
- Unknown signature recovery never passes via strict=False.

### Related work

OTP-003, OTP-014

## OTP-016 — Execution-kind semantics

**Status:** Open; policy selected

**Release target:** 0.1 def/coroutine policy; later expansion

### Problem

Coroutine functions, awaitable-returning def, generators, async generators, and callable objects have different runtime representations.

### Selected policy

0.1 requires matching ordinary def/coroutine async def declaration kinds in addition to signature/type relations. This is a Stipulate policy, potentially stricter than typing assignability.

### Acceptance tests

- Test coroutine versus ordinary def in both directions and prevent double wrapping of coroutine result annotations.
- Classify generators/async generators/callable objects explicitly as unsupported until handlers pass.
- Decorator metadata cannot silently erase execution-kind uncertainty.

### Related work

OTP-003, OTP-004, OTP-015

## OTP-017 — Nested Protocol annotations

**Status:** Open

**Release target:** Phase 2

### Problem

Protocols in parameter/return annotations require structural type relations, not recursive execution of candidate values.

### Selected policy

Do not conflate annotation assignability with runtime-value validation. The initial nominal table does not imply nested Protocol support.

### Acceptance tests

- Test nested concrete-to-Protocol relations, mutually recursive contracts, and termination.
- Use cycle-aware relation state rather than unconditional success for a visited pair.
- No nested candidate return value is obtained by calling a method.

### Related work

OTP-004, OTP-005

## OTP-018 — Self binding

**Status:** Open

**Release target:** Phase 4; required only if advertised

### Problem

Self depends on enclosing and implementing types, inheritance, and method binding.

### Selected policy

Preserve structural Self relationships rather than choosing the interface or candidate class by convenience.

### Acceptance tests

- Use specification fixtures for parameters, returns, inherited methods, and class methods.
- Record the binding environment and prove consistent substitution across a contract.

### Related work

OTP-004, OTP-006

## OTP-019 — Typed kwargs and TypedDict unpacking

**Status:** Deferred

**Release target:** Phase 4

### Problem

Unpack[TypedDict] encodes keyword names, requiredness, and value types jointly.

### Selected policy

No support until the callable algorithm preserves these relationships.

### Acceptance tests

- Test required/optional keys, Required/NotRequired, ordinary kwargs, collisions, and missing coverage.
- Derive fixtures from the typing specification.

### Related work

OTP-003, OTP-004, OTP-009

## OTP-020 — Mutation and snapshot refresh

**Status:** Open; policy selected

**Release target:** 0.1 blocker

### Problem

Classes and annotation dependencies can change after compilation; validated candidates can change after checking.

### Selected policy

Contracts are snapshots. No automatic mutation tracking or candidate-success cache. Contract(Storage, refresh=True) creates a new snapshot; retained old contracts remain unchanged.

### Acceptance tests

- Test interface mutation with and without refresh, failed refresh, and multiple retained snapshots.
- Test candidate mutation observed on the next check.
- Document changes to referenced annotation types and namespaces.

### Related work

OTP-021

## OTP-021 — Cache ownership and concurrency

**Status:** Open; retention trap reproduced in design probe

**Release target:** 0.1 blocker

### Problem

Weak keys do not prevent leaks when cached values retain their declaration keys, directly or through annotations.

### Selected policy

Use weak keys and weak IR values globally; a live Contract strongly owns its snapshot. Custom namespaces bypass shared caching. Locks protect cache operations, not user evaluation.

### Acceptance tests

- Test collection of local and self-referential interfaces after all owners disappear.
- Test IR reuse while retained, expiry otherwise, and no cached traceback retention.
- Stress concurrent first-use, refresh, and validation without mutable shared candidate state.
- Do not require exactly-once annotation evaluation under races.

### Related work

OTP-005, OTP-020

## OTP-022 — Diagnostic contract and usability

**Status:** Open; initial policy selected

**Release target:** 0.1 initial fields/codes; 1.0 stability

### Problem

Users need both an immediately understandable repair and stable machine-readable failure/uncertainty records.

### Selected policy

ERROR_MODEL.md defines initial exceptions, evidence, export fields, code categories, ordering, and prose stability.

### Acceptance tests

- Verify JSON-compatible exports, immutable internal records, independent export copies, and stable locations/codes.
- Render incompatible and unknown findings differently.
- Suggest permissive validation only for allowlisted uncertainty.
- Test ContractError.errors() rejected unknowns versus result.errors() incompatibilities.

### Related work

OTP-013, OTP-028

## OTP-023 — Canonical schema and identity

**Status:** Open

**Release target:** Phase 5; not public 0.1

### Problem

Portable serialization must represent semantics and nominal identity without leaking arbitrary runtime objects or executing imports during loading.

### Selected policy

Internal IR is not public schema. Freeze versioning, portability, normalization, defaults, and ignored metadata before schema()/fingerprint() publication.

### Acceptance tests

- Deterministic member/union/type ordering and versioned canonical output.
- Local/dynamic nominal types are rejected or marked non-portable rather than serialized with unstable repr.
- Separate default presence from behavior-changing default values and ignored Annotated constraints.
- Round trips only if deserialization is actually supported; no automatic arbitrary import/evaluation.
- Fingerprint differences do not imply incompatibility.

### Related work

OTP-004, OTP-005; additional type-feature gates only for forms actually serialized

## OTP-024 — Performance baseline

**Status:** Open

**Release target:** Before beta; justified guarantees by 1.0

### Problem

Requirement caching does not remove repeated candidate introspection costs.

### Selected policy

Measure cold compilation and candidate inspection separately. Favor retained Contract reuse; no premature native implementation.

### Acceptance tests

- Benchmark success, mismatch, uncertainty, temporary/retained contracts, large interfaces, and annotation depth.
- Separate performance tracking from fragile correctness thresholds.
- Optimizations must preserve evidence and mutation policy.

### Related work

OTP-021

## OTP-025 — Runtime and packaging matrix

**Status:** Open; minimum and initial targets selected

**Release target:** 0.1 blocker

### Problem

Protocol, annotation, and introspection behavior varies across Python releases.

### Selected policy

Minimum CPython 3.11; initial release test targets 3.11–3.14. No runtime support is advertised before complete tests pass. PyPy is not a 0.1 claim.

### Acceptance tests

- Run compiler, checker fixtures, candidate validation, evidence, caching, and installed-distribution tests across the supported matrix.
- Test newer deferred annotation behavior rather than relying on import success.
- Record tested checker/dependency versions and required flags.

### Related work

OTP-005, OTP-010, OTP-026

## OTP-026 — TypeForm public Contract boundary

**Status:** Design probe passes recorded local configurations; package implementation open

**Release target:** 0.1 blocker

### Problem

The constructor must tie a Protocol declaration to validate() return type without the concrete-class restriction of type[T].

### Selected policy

Use TypeForm[T]. Preserve Contract(Storage) inference without caller-selected unrelated type parameters or public Any leakage.

### Acceptance tests

- Both supported checkers infer Contract[Storage] and validate() -> Storage.
- Reject mismatched explicit generic arguments and invalid type-form inputs statically; reject unsupported declaration forms at runtime.
- Record mypy TypeForm flags and typing_extensions requirements.
- Reproduce design probes against installed wheel and sdist with no source-tree shadowing.

### Related work

OTP-010, OTP-025

## OTP-027 — Universal directional evolution

**Status:** Open; semantics selected

**Release target:** Phase 6

### Problem

Gradual assignability is weaker than a guarantee that all old implementations or consumers remain compatible.

### Selected policy

Use explicit universal-guarantee relation context with shared normalized rules. Implementers compare old to new; consumers compare new to old. Any-dependent assumptions remain unknown.

### Acceptance tests

- Test the change table in CONTRACT_ENGINE.md in both directions.
- Do not infer transitivity through Any or unsupported forms.
- Test breaking=True for a known incompatible direction, False only when both compatible, None otherwise.
- CI rejects unknown required directions by default and never treats falsey unknown results as approval.

### Related work

OTP-004, OTP-023, OTP-028

## OTP-028 — Evidence, truthiness, and enforcement

**Status:** Open; exact policy selected

**Release target:** 0.1 blocker

### Problem

A result must distinguish metadata conclusions from caller willingness to tolerate uncertainty.

### Selected policy

CONTRACT_ENGINE.md owns the exact status/completeness/truthiness/acceptance table. No public assurance enum. Strict is default; permissive accepts only annotation_missing and gradual_type.

### Acceptance tests

- Test every truth-table row, mixed mismatches/unknowns, empty contracts, and complete failures.
- Test AND/OR relation logic and dependent unassessed obligations.
- check() findings do not change with enforcement policy; accepted() and validate() share one function.
- bool(UNKNOWN) is false and no unsupported/uninspectable capability is silently accepted.

### Related work

OTP-013, OTP-022

## OTP-029 — Developer experience and report presentation

**Status:** Open; presentation specification and illustrative scenarios selected

**Release target:** 0.1 presentation; installed examples and report verification

### Problem

Accurate findings are insufficient if users cannot understand the failed operation, distinguish unknown evidence, or discover the right next step. A polished UI must not create a second compatibility engine.

### Selected policy

EXPERIENCE_DESIGN.md owns user journeys, result language, plain-text rendering, progressive disclosure, and optional usability research. Result rendering is a pure view over evidence. The 0.1 UI is the Python API, editor types, reports, and documentation; a separate dashboard is not planned.

### Acceptance tests

- Exercise compatible, incompatible, unknown, mixed, definition-failure, and empty-contract reports using the actual implementation.
- Verify strict/permissive decisions against the engine's acceptance table; permissively accepted UNKNOWN remains UNKNOWN.
- Verify plain str/repr output, no hidden logging or candidate repr calls, control-character escaping, and readable 60/80-column output.
- Use symbolic call-shape counterexamples only when established without candidate execution.
- Type-check and execute the quickstart against the installed package; a design stub does not satisfy execution.
- Participant research is optional and does not block the phase 0.1 beta experience gate.

### Related work

OTP-022, OTP-026, OTP-028; later CLI presentation also depends on OTP-023/027.

## Release gates

0.1 must satisfy OTP-003, 004, common 005, 010, instance 011, basic 012, 013, explicit-policy 014, 015, basic 016, 020, 021, initial 022, baseline 024, 025, 026, 028, and the 0.1 presentation requirements of 029 for exactly the roadmap subset.

OTP-001/002 are independent experimental shorthand gates. OTP-006/007, 008/009, 017/018/019, 023, and 027 are later feature gates; they are mandatory only before the corresponding support is advertised. A stable 1.0 can document a deliberately bounded subset.

## Maintenance

For a resolved item, commit acceptance tests, update the focused specification and durable decision, record the actual release and test matrix, and mark it resolved. Preserve the historical problem statement or link its superseding decision/archive. Update release scope in the same change when a feature moves stages.
