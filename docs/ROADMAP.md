# Roadmap and 0.x Release Phases

This is the release-scope document. It answers one question for every version: **what can a user depend on after installing it?**

Versions are capability gates, not calendar promises. A phase ships only when its user journeys, semantics, diagnostics, typing, documentation, and compatibility tests pass. If a feature is not listed as supported for a release, Stipulate reports it explicitly as unsupported or unknown; it does not quietly approximate it.

The other planning documents have narrower authority:

- [DESIGN_DECISIONS.md](DESIGN_DECISIONS.md) records durable policy.
- Focused documents define behavior and terminology.
- [OPEN_TECHNICAL_PROBLEMS.md](OPEN_TECHNICAL_PROBLEMS.md) records unresolved acceptance work.
- [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md) orders the engineering slices inside a release.
- [EXPERIENCE_DESIGN.md](EXPERIENCE_DESIGN.md) defines the user experience and usability bar.

The repository is currently design-stage. The design probes are useful evidence about typing and Python behavior, but no 0.x release claim is complete until the actual installed package passes the gates below.

## Release principles

Every release should:

1. Preserve the public behavior already promised by earlier releases, or document a deliberate 0.x breaking change.
2. Add a complete user task rather than exposing an unfinished internal subsystem.
3. Keep the compatibility result, enforcement policy, and presentation separate.
4. Preserve `UNKNOWN` when metadata is insufficient; permissive acceptance must never relabel it as `COMPATIBLE`.
5. Prefer a small, correct supported subset over broad, surprising acceptance.
6. Test the installed wheel and source distribution across the advertised Python and checker matrix.

The 0.x series may evolve APIs and diagnostics, but correctness fixes that reject previously accepted candidates must be called out clearly. No version may claim behavioral execution guarantees that Stipulate does not provide.

## Version map

| Release | Product promise | Main user-facing addition | Primary gates |
| --- | --- | --- | --- |
| **0.1** | Check a standard Protocol against a live implementation | `Contract(Protocol).validate()` and `.check()` | Core contract engine, evidence, errors, typing, supported subset |
| **0.2** | Make the core dependable in real application boundaries | Operational hardening, richer diagnostics, stable instance/property policy | Lifecycle, concurrency, inspection, usability, performance baselines |
| **0.3** | Cover the ordinary Python typing patterns users reach for next | Nested protocols, aliases, class/static methods, selected descriptors and decorators | Expanded conformance corpus and explicit runtime policies |
| **0.4** | Make generic contracts useful | `TypeVar` specialization, bounds, constraints, and variance | Coherent binding and substitution across every member |
| **0.5** | Handle advanced callable declarations deliberately | Overloads, `Self`, `ParamSpec`, and selected generator/awaitable forms | Independent specification-driven callable gates |
| **0.6** | Turn contracts into portable artifacts | Versioned `schema()` and `fingerprint()` | Canonical identity, portability, deterministic serialization |
| **0.7** | Make contract evolution reviewable | Directional `compare()` and `CompatibilityReport` | Universal implementer/consumer analysis and unknown-safe policy |
| **0.8** | Make evolution usable in automation | Snapshots, semantic diff, optional CLI, CI exit policy | Schema and evolution integration tests |
| **0.9** | Prepare a trustworthy 1.0 | API, diagnostics, typing, performance, and documentation stabilization | Release-candidate audit and migration guidance |
| **1.0** | Provide a stable bounded contract engine | Stable supported subset and compatibility policy | Long-term compatibility guarantees |

The numbers are intentionally sequential. A later release can be skipped if its scope is small enough to combine with the next phase, but a feature cannot be promoted merely because its code exists.

### Gate mapping

| Release | Required technical problems |
| --- | --- |
| 0.1 | OTP-003, 004, 005 (common cases), 010, 011 (instances), 012 (basic cases), 013, 014 (explicit limitation), 015, 016 (basic coroutine policy), 020, 021, 022 (initial contract), 024 (baseline), 025, 026, 028, and the 0.1 presentation work in OTP-029 |
| 0.2 | The remaining 0.1 hardening work, especially OTP-005, 014, 015, 020, 021, 022, 024, 025, and 029 |
| 0.3 | OTP-005 expansion, 014, 015, 017, and the class/static portions of 012 |
| 0.4 | OTP-006 and OTP-007 |
| 0.5 | OTP-008, 009, 018, and 019, each independently before that construct is advertised |
| 0.6 | OTP-023 and every type-feature gate needed by the published schema |
| 0.7 | OTP-027, plus the shared relation and gradual-type work in OTP-004 and OTP-028 |
| 0.8 | The schema/evolution gates from 0.6–0.7 and release-specific snapshot/CLI acceptance tests |
| 0.9 | All unresolved issues for the frozen advertised subset, including OTP-022, 024, 025, and 029 |

This mapping is a planning aid, not permission to mark an OTP resolved early. The register remains authoritative about acceptance evidence and status.

## 0.1 — Core validation

### User outcome

A developer with an existing `typing.Protocol` can validate a dynamically loaded implementation, receive the original object with the Protocol type preserved, and understand a mismatch immediately.

### Supported surface

- `Contract(Protocol)` with `TypeForm[T]` inference.
- `contract.validate(candidate, strict=True)` and `contract.check(candidate)`.
- Ordinary bound instance methods and the explicit 0.1 coroutine `async def` policy.
- Deterministic call-shape checks for positional-only, positional-or-keyword, keyword-only, defaults, `*args`, and `**kwargs`.
- Directional parameter and return relations for the finite type subset in [TYPE_SYSTEM.md](TYPE_SYSTEM.md): nominal types, `None`, unions, `Literal`, `Annotated` underlying types, numeric promotions, and the documented collection origins.
- Declared plain attributes and standard read/write properties without invoking getters.
- `COMPATIBLE`, `INCOMPATIBLE`, and `UNKNOWN` results with independent completeness.
- Strict-by-default enforcement, the narrowly allowlisted `strict=False` policy, immutable evidence, `ContractError`, and `ContractDefinitionError`.
- Trusted and raw annotation policies, explicit namespace inputs, retained snapshots, weak global cache keys and values, and explicit refresh behavior.
- Plain, deterministic result and exception rendering, quickstart documentation, and installed-package typing fixtures.

### Deliberately outside 0.1

General user-defined generics, overloads, nested Protocol annotations, `Self`, advanced callable packs, custom/dynamic descriptors, class-object preflight, current-value validation, schema/fingerprint, comparison, CLI, snapshots, and Pydantic integration.

### Exit gate

The exact 0.1 gate is the intersection of the feature matrix above and the release-blocking OTPs listed in [OPEN_TECHNICAL_PROBLEMS.md](OPEN_TECHNICAL_PROBLEMS.md). The quickstart and report scenarios must run against the real package. Pyright strict, the supported mypy configuration, CPython 3.11–3.14 tests, lifecycle tests, and the initial usability exercise must pass.

## 0.2 — Production-boundary hardening

### User outcome

A framework author can keep one Contract instance for repeated plugin checks and trust the result, error, and cache behavior under ordinary concurrency and mutation.

### Scope

- Complete the 0.1 matrix with measured cold-compilation and warm-validation baselines.
- Harden annotation resolution, decorator/signature recovery, forward-reference diagnostics, and dynamic-member uncertainty.
- Finish plain storage, standard properties, slots, and class-versus-instance documentation for the supported cases.
- Improve multi-error reports, long-name wrapping, sanitized metadata rendering, and structured export ergonomics without changing semantic status.
- Add explicit operational guidance for refresh, mutation, custom namespaces, and retained Contract ownership.
- Improve ergonomics through the existing Contract, result, and error surfaces only when a demonstrated repeated task justifies the change; do not create parallel validator APIs.

### Exit gate

No known retention path through cache values, failed compilation tracebacks, or annotation graphs; concurrent first-use and refresh tests pass; the quickstart task and the five-person usability exercise are repeatable on the installed package; benchmark trends are recorded without turning them into unsupported guarantees.

## 0.3 — Ordinary typing and member expansion

### User outcome

Most conventional Protocol declarations can be checked without surprising treatment of common aliases, nested structural types, binding forms, or well-behaved decorators.

### Scope

- Nested Protocol/interface annotations with cycle-aware relations, without recursively invoking candidate methods or validating returned values.
- Common type aliases, newer alias forms where runtime metadata is available, and better forward-reference provenance.
- Class methods and static methods with explicit binding rules.
- Selected standard descriptors and decorator patterns whose externally exposed signatures can be recovered safely.
- A documented policy for dynamic attributes, custom descriptors, extension callables, and unsupported class-object validation.
- Broader checker fixtures and a versioned supported-type table.

### Exit gate

Each new member or type form has positive, negative, unknown, definition-error, checker, and Python-version tests. Unsupported dynamic behavior remains visibly unsupported; no new handler calls user code to discover compatibility.

## 0.4 — Generic contracts

### User outcome

A generic Protocol can be specialized once and have its type variables enforced consistently across parameters, returns, attributes, and inherited members.

### Scope

- `TypeVar` binding and substitution, including multiple variables.
- Bounds, constraints, generic inheritance, and specialization before candidate inspection.
- Explicit and inferred variance where runtime metadata and the typing specification provide enough information.
- Coherent recursive substitution and clear behavior for unspecialized contracts.
- Generic collection relations beyond the finite 0.1 origin table where semantics are proven.

### Exit gate

No silent type-argument erasure. Conflicting bindings, unknown variance, and unsupported specializations have explicit outcomes. The same binding environment is used for every member and is covered by specification-oriented fixtures.

## 0.5 — Advanced callable contracts

### User outcome

Users can express richer callable APIs without Stipulate flattening away parameter correlations or promising support it cannot inspect.

### Scope

Promote each construct independently, only when its own gate passes:

- overload sets and implementation coverage;
- `Self` relationships;
- `ParamSpec` and `Concatenate`;
- typed `**kwargs` with `Unpack[TypedDict]`;
- `TypeVarTuple` and other parameter packs;
- generator and async-generator execution kinds;
- selected callable-object, awaitable, and context-manager forms.

### Exit gate

Every advertised construct has a normalized representation, a specification-based relation algorithm, runtime metadata policy, and negative tests for missing or misleading metadata. Unsupported forms remain explicit unknowns or definition errors.

## 0.6 — Contract artifacts

### User outcome

A team can inspect, persist, identify, and exchange a contract without depending on Python source formatting or unstable object representations.

### Scope

- Versioned `Contract.schema()` with an explicitly documented schema format.
- Deterministic `Contract.fingerprint()` over canonical semantic content.
- Portable nominal type identity, aliases, unions, defaults, recursive references, generic bindings, and ignored metadata rules.
- Safe schema inspection that does not automatically import or execute arbitrary references.
- Documentation and examples for generated docs, manifests, and baseline storage.

### Exit gate

Schema versioning, portability, canonical ordering, round-trip behavior where supported, and fingerprint compatibility policy are tested. A fingerprint difference is never presented as a compatibility verdict.

## 0.7 — Interface evolution

### User outcome

A library author can compare two explicit contracts and see whether a change affects existing implementers, existing consumers, or both.

### Scope

- `Contract(old).compare(Contract(new))` and `CompatibilityReport`.
- Shared normalized relations with an explicit universal-guarantee context.
- Separate implementer and consumer results.
- Three-valued breaking state: true for a known incompatible direction, false only when both directions are compatible, and unknown otherwise.
- Change records for members, call shapes, mutability, execution kind, and supported type relations.

### Exit gate

The change table in [CONTRACT_ENGINE.md](CONTRACT_ENGINE.md) passes in both directions. Any-dependent or unsupported relations cannot certify a universal guarantee. Unknown required directions remain visible and fail closed under the default CI policy.

## 0.8 — Automation and semantic CI

### User outcome

A team can keep a contract baseline in version control and review semantic changes in local development and CI.

### Scope

- Snapshot format built on the versioned schema.
- Semantic diff and human-readable change reports.
- Optional `stipulate[cli]` package with `snapshot`, `check`, and `diff` commands.
- Explicit JSON output, plain redirected output, documented exit-code categories, and selected implementer/consumer policy.
- CI examples that reject incompatible and unknown required directions without importing arbitrary snapshot references.

### Exit gate

CLI output and Python results are generated by the same engine. JSON contains no terminal styling, exit codes are stable for the release, snapshots are deterministic, and unknown policy is explicit in every example.

## 0.9 — Release candidate

### User outcome

A team can adopt Stipulate with confidence that the documented subset, diagnostics, checker behavior, and migration policy will not shift unexpectedly at 1.0.

### Scope

- Freeze the advertised supported-type/member matrix and public API names.
- Complete cross-version and installed-distribution testing.
- Audit structured error fields/codes, schema versions, CLI behavior, and deprecation paths.
- Publish performance baselines, limitations, security/evaluation notes, and migration guidance.
- Run the full usability exercise with actual release-candidate artifacts.
- Keep Interface shorthand and Pydantic integration separately gated; neither is promoted by proximity to 1.0.

### Exit gate

No release-blocking OTP remains unresolved for the advertised subset. Remaining unsupported typing constructs are named. All public examples are executable or explicitly labeled conceptual, and a release audit can trace every promise to evidence.

## 1.0 — Stable bounded contract engine

1.0 does not mean implementing every Python typing feature. It means the supported subset, result semantics, enforcement defaults, diagnostics, schema policy, Python matrix, and deprecation behavior are stable enough for dependents to build on. Advanced constructs can remain unsupported when the limitation is explicit and tested.

Pydantic integration remains optional and post-1.0. Interface shorthand is promoted only if its independent checker and runtime gates pass; otherwise the stable API remains standard Protocol plus Contract.

## Cross-release acceptance checklist

Before cutting any 0.x release, attach one evidence bundle containing:

- the exact supported feature matrix for that version;
- runtime and checker versions, flags, and installed wheel/sdist results;
- positive, negative, unknown, and definition-error tests for each advertised feature;
- structured diagnostic and presentation checks;
- cache, mutation, annotation-evaluation, and concurrency results;
- benchmark measurements with their environment;
- documentation example runs and link checks;
- usability observations for any changed primary journey;
- unresolved limitations and their next release target.

If the bundle is incomplete, move the feature or the release gate explicitly. Do not convert missing evidence into a green status.
