# Testing Strategy

## Principle

Test semantic obligations, not merely code paths. A feature is supported only when its documented positive, negative, unknown/definition-error, checker, and Python-version cases pass. Keep intentionally invalid fixtures separate from valid examples.

## Existing design evidence

../design_probes/ contains static API declarations and isolated Python behavior checks. It demonstrates TypeForm inference and records rejected alternatives; it does not validate Stipulate at runtime. Its README records commands, versions, and expected limitations.

Replace assumptions with installed-package tests as implementation lands. Run wheel and sdist consumer fixtures outside the source tree so imports cannot accidentally use local code or missing stub files.

## Public typing corpus

Assert exact inferred Contract[Protocol] and validation return types with assert_type. Test incompatible explicit generic arguments and invalid structural implementations. Record the mypy TypeForm feature flag where required. Do not count reveal_type output as success when the same file has errors.

Preserve regressions for the type[T] Protocol-value disagreement and implicit Protocol-subclass downgrade. Experimental Interface fixtures must prove clean member sets, class-side methods, precise types, explicit structural composition, and no required checker plugins.

## Runtime layers

- Compilation: supported declarations, inheritance, conflicting overrides, type normalization, source metadata, definition diagnostics.
- Candidate inspection: standard binding, actual storage presence, properties without getter execution, unavailable signatures, wrapper cycles, dynamic dispatch uncertainty.
- Relations: every parameter kind, defaults, variadics, variance, literals, unions, numeric promotions, supported origin substitutions, unsupported identity fallback rejection.
- Results: all status/completeness combinations, empty contracts, OR/AND truth tables, independent mismatches plus unknowns, dependent unassessed facts.
- Enforcement: strict default, exact permissive allowlist, no mutation of evidence when accepted, identity of returned objects, both exception paths.
- Diagnostics: stable codes/locations, deterministic ordering, actionable unknown wording, JSON-safe exports, no internal type objects leaked.

## Annotation and execution tests

Use harmless counters to verify trusted annotation evaluation can execute expressions and raw mode does not request it. Cover eager, string, and deferred annotations across supported versions. Test forward refs, TYPE_CHECKING-only names, explicit local namespaces, recursive unsupported forms, and missing implementation annotations.

Counters on methods, properties, __getattr__, and custom descriptors must remain untouched by supported core checks. Unsupported custom dispatch must yield uncertainty rather than being called to obtain evidence. Do not claim a general sandbox from these tests.

## Lifecycle and concurrency

Test weak keys AND weak values, self-referential declaration metadata, failures without cached tracebacks, custom namespaces, live snapshot ownership, collection after owners disappear, refresh behavior, candidate mutation, and concurrent first-use/refresh. Do not assume annotation evaluation runs exactly once under races.

## Property and differential tests

Generate valid callable signatures and compare bounded call-shape oracles against the deterministic algorithm. Use simple nominal graphs and supported collection/union types. Include incompatible parameter narrowing and return widening as mutation-sensitive properties.

Do not assert transitivity for gradual assignability through Any. For fully static supported relations, test appropriate reflexivity and transitivity with explicit exclusions for policy-based unknowns. Oracle uncertainty remains uncertainty, not a forced boolean.

The typing specification is the semantic oracle; Pyright and mypy are conformance targets. Runtime type-checking libraries may inform narrow tests but are not assignability authorities.

## Later schema/evolution tests

Canonical schema tests cover deterministic ordering, portable nominal identities, ignored metadata, defaults, recursion, versioning, and round trips only if a loader ships. Evolution tests cover both directions, concrete change tables, gradual uncertainty, mixed incompatible/unknown evidence, and fail-closed CI. Fingerprint equality alone is not a compatibility proof.

## Documentation and performance

Promoted examples run and type-check against the installed package. Conceptual, experimental, and future snippets are explicitly labeled. Check internal links and API names during doc changes.

Benchmark cold compilation, warm retained contracts, candidate inspection, errors, unknowns, and large interfaces separately. No fragile wall-clock threshold in correctness CI. Mutation testing and wider fuzzing follow the first trustworthy corpus.

## Experience verification

OTP-029 adds a pure-presenter boundary, illustrative report scenarios, and a measured public-beta usability exercise. Test all report states, exact semantic counts, unknown acceptance without status changes, plain str/repr output, wrapping at 60/80 columns, escaping untrusted metadata, and absence of candidate repr/str/getter calls. Use independent engine-produced records for integration tests; rendering fixture text is not proof of compatibility correctness.

The quickstart must execute and preserve inferred types against the installed package. Design-stage checks against contract_api.pyi only prove the proposed static surface. Record usability observations separately from automated checks and never claim participant results that were not collected.
