# Implementation Plan

## Objective and scope

Deliver an approachable structural-contract library whose type inference, diagnostics, and runtime semantics reinforce each other. ROADMAP.md owns the supported 0.1 matrix. EXPERIENCE_DESIGN.md owns the user journeys and presentation bar. The current repository contains specifications and design probes, not a working package.

For the implementation-ready contract for the entire 0.1 release, use [PHASE_0_1_IMPLEMENTATION_CONTRACT.md](PHASE_0_1_IMPLEMENTATION_CONTRACT.md). Its active AC-001 through AC-029 plus AC-031 (AC-030 withdrawn) and P1 through P8 refine the slices below without promoting later-release features or resolving implementation gates from documentation alone.

Each slice must demonstrate a complete user task with a positive case, meaningful failure or uncertainty, precise public types, and an executable example. A slice can be deliberately narrow internally; only the complete roadmap matrix is advertised as 0.1 support.

## Permanent engineering rules

Pyright strict passes from the first implementation commit. Public fixtures also pass the pinned mypy configuration, including its TypeForm flag when required. No public Any leakage, consumer ignores, or equality fallback for unsupported forms.

Keep immutable requirement IR, ephemeral candidate evidence, enforcement policy, and presentation separate. A view must not reimplement the compatibility engine. Tests verify semantic outcomes independently of rendered wording.

## Slice 1 — A reproducible typed installation

**User outcome:** An installed package recognizes Contract(Storage) as Contract[Storage] and preserves Storage through validate().

Create package metadata, py.typed, source/test directories, pytest, Ruff, Pyright strict, mypy fixtures, and distribution CI. Prove TypeForm[T] constructor inference, negative type-argument cases, and explicit Protocol composition outside the source tree using installed wheel and sdist builds.

**Evidence to review:** Exact type assertions, expected negative diagnostics, clean-environment installation logs, and pinned checker/dependency settings. A stub proves only static shape until runtime behavior exists.

**Exit gate:** Reproducible package and checker results on the initial CPython 3.11–3.14 targets, with no advertised runtime feature inferred merely from import success. Maps to OTP-010/025/026.

## Slice 2 — First validation, first useful failure

**User outcome:** A fully annotated single-method Protocol accepts a compatible implementation, rejects an incompatible parameter, and explains a missing candidate return annotation.

Implement the smallest real compiler/IR, candidate inspection, nominal parameter/return relation, immutable evidence, three-valued result, enforcement function, ContractError/ContractDefinitionError, and plain result/exception presenter. Use strict defaults from day one. Return the original candidate on success.

This slice initially supports only the narrow forms needed for its example; unsupported forms fail explicitly. Do not simulate a complete engine with unconditional casts or return an unimplemented happy path.

**Evidence to review:** The quickstart runs against the implementation. Compatible, incompatible, unknown, invalid-definition, and empty-contract examples render accurately. print(result) has no additional candidate access. The basic runtime-to-error loop can be demonstrated before the broader type system is built.

**Exit gate:** Tests agree on bool(result), complete, accepted(strict=...), exception contents, and inferred return type. Maps to OTP-003/004/013/022/026/028/029 for this narrow slice.

## Slice 3 — Every legal call

**User outcome:** Plugin authors can understand and repair signature failures involving keyword names, parameter kinds, defaults, and variadics.

Expand deterministic call-shape containment, standard bound-method normalization, exposed-signature precedence, and coroutine-kind policy. Add wrapper-cycle protection, unsupported-signature evidence, and independent multi-error aggregation.

Use a symbolic required-call example when the algorithm can establish one without executing the candidate. Keep generated behavioral calls outside the core.

**Evidence to review:** Specification fixtures and bounded property-test oracles cover all parameter-kind interactions. The call-shape report scenario is produced by real code and explains a concrete failed obligation.

**Exit gate:** No sampled-call production algorithm, no swallowed inspection/internal failures, and no permissive acceptance of unknown signatures. Maps to OTP-003/014/015/016/022.

## Slice 4 — The promised type subset

**User outcome:** Ordinary annotated plugins using the roadmap's unions, literals, nominal types, and supported collections receive accurate directional outcomes.

Implement exactly the finite type/origin table in TYPE_SYSTEM.md. Cover numeric promotions, Literal value/type identity, Annotated metadata treatment, collection variance/substitution, deliberate Any evidence, and unsupported-identity rejection.

Complete common trusted/raw annotation resolution with correct requirement/candidate namespaces, TYPE_CHECKING-name limitations, explicit local namespaces, and version-specific deferred annotations. Unsupported recursive and advanced forms terminate with diagnostics.

**Evidence to review:** A specification-indexed corpus showing expected, Pyright, mypy, and Stipulate outcomes; intentional policy differences; annotation-effect tests; and mixed incompatible/unknown results.

**Exit gate:** Every promised type form has positive, negative, and unknown/definition-error cases. Gradual assignability is never treated as universally transitive. Maps to OTP-004/005/010/013/028.

## Slice 5 — Supported storage and properties

**User outcome:** Implementations with documented plain attributes and standard properties can be checked without reading through user getters.

Add declared read/write capabilities and separate presence checks. Test read covariance, write contravariance, annotations-only storage, uninitialized slots, and mismatches hidden by a currently matching value. Unsupported dynamic dispatch, descriptors, and class-object candidates remain explicit limitations.

**Evidence to review:** Getter/descriptor/hook counters remain untouched. The diagnostic identifies whether presence, read type, write type, or inspectability is the problem.

**Exit gate:** No current-value proof of writable declarations and no implicit value validation. Maps to OTP-011/012/014/022.

## Slice 6 — Reuse, mutation, and reliability

**User outcome:** Framework authors retain one Contract and safely check many independent candidates, with explicit behavior when declarations change.

Add weak keys and weak IR values in the shared cache, snapshot refresh, custom-namespace cache bypass, and concurrent publication. Keep candidate state per call; do not cache successful candidates or exception tracebacks.

**Evidence to review:** Collection of temporary/self-referential declarations, live-owner retention, independent old/new snapshots, failed refresh, concurrent first use, and candidate mutation. Profiles distinguish requirement compilation from candidate inspection.

**Exit gate:** Lifecycle/concurrency suites pass and benchmark baselines exist without unmeasured latency claims. Maps to OTP-020/021/024.

## Slice 7 — Public beta experience

**User outcome:** A developer unfamiliar with the engine can validate an implementation, repair a mismatch, and interpret missing evidence from the shipped documentation.

Complete all roadmap rows and run the scenario catalogue against real engine results. Check 60/80-column reports, long identifiers, terminal-control escaping, color-independent meaning, compact repr, and no implicit logging. Publish exact checker configuration and known limitations alongside the quickstart.

Participant testing is optional follow-up work and does not block phase 0.1. Fix demonstrated documentation or diagnostic issues without weakening compatibility policy.

**Evidence to review:** Diagnostic examples, full-matrix CI, installed-package documentation execution, and a supported/unsupported feature inventory.

**Exit gate:** All 0.1 semantic gates and OTP-029's beta experience criteria pass. There are no known cases where a supported incompatible declaration is accepted or unsupported evidence is presented as established compatibility.

## Slice 8 — 0.1 release decision

Review one release evidence bundle containing the feature matrix, exact runtime/checker versions, conformance results, example runs, lifecycle tests, performance measurements, and documented remaining limits.

Every advertised feature must trace to tests. Any unresolved release-blocking correctness or experience issue blocks publication; move scope explicitly in the roadmap and focused documents if needed. A screenshot, happy-path demo, or internal module completion is not a release gate.

## Scope and prioritization rule

Prioritize work that closes a demonstrated failure in the primary journeys or a correctness gate for the supported subset. Add a feature only with its user problem, semantics, diagnostic behavior, release target, and acceptance evidence defined. Do not let optional CLI, Pydantic, native optimization, or Interface research delay the Contract core.

Track each work item with: user outcome, supported cases, unknown/error behavior, relevant OTP, evidence artifact, and current blocker. Establish time estimates after early slices provide measured implementation throughput; do not present invented dates or speed targets as commitments.

## Later delivery

After the core, separately expand ordinary member/annotation support, user generics, and advanced callables. Stabilize canonical schema before schema()/fingerprint(), then prove directional evolution before compare()/CompatibilityReport. CLI/snapshots consume those APIs. Pydantic remains optional and post-1.0.

The Interface shorthand is an independent research gate. Promotion requires precise class-side typing, structural composition, clean member discovery, and installed-package tests in both checkers without consumer workarounds.

## Definition of done

A developer can define a Protocol, validate a candidate, understand and repair a failure, and deliberately handle uncertainty. The package preserves precise types and the original object, passes its complete advertised test matrix, and communicates exactly what available declarations establish.
