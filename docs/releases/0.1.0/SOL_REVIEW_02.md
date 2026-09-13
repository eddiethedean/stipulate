# Sol production re-review 02

Verdict: **NEEDS FIXES**.

Reviewed remediation: `3079e9f819b21857654502be811f1d92e5ea8d15`, against review 01 at `40cfd0e`. This is the first implementation attempt for SOL-001 through SOL-009. The approved phase 0.1 contract remains unchanged; AC-030 remains withdrawn. No production implementation, benchmark measurements, configuration, or previous verification artifact was modified during this review.

Read the approved architecture/implementation contract, focused type/storage/performance specifications, implementation report, review 01, remediation diff, relevant production paths, existing tests, workflows, and the implementation handoff in this conversation. The original implementation report is historical; its 160-test count is not used as the current result.

All eleven review-01 checks now pass. Five blockers are VERIFIED FIXED. Four are PARTIALLY FIXED because their required invariants remain violated beyond the original examples. Stable finding IDs are preserved. No newly introduced substantive regression or unrelated follow-up was established.

## Acceptance criteria

| AC | Status | Evidence or remaining blocker |
| --- | --- | --- |
| AC-001 | VERIFIED | Canonical wheel/sdist metadata; eight successful clean installed CI consumers |
| AC-002 | VERIFIED | Pinned installed positive/negative Pyright and mypy consumers on all minors/artifacts |
| AC-003 | VERIFIED | SOL-002 and SOL-009 fixed; existing invalid/unsupported definition corpus passes |
| AC-004 | VERIFIED | Identity-only owner exclusions; override/composition/diamond corpus passes |
| AC-005 | PARTIALLY SATISFIED | SOL-006 still accepts an intercepted writable property; SOL-001 can execute metadata equality |
| AC-006 | VERIFIED | Configuration-before-work, exact booleans, namespace copies, public signatures and identity |
| AC-007 | VERIFIED | Exact legal-call partition and independent Python-call oracle corpus |
| AC-008 | VERIFIED | Binding, explicit/wrapped precedence, malformed metadata and cycle corpus |
| AC-009 | VERIFIED | SOL-009 fixed; coroutine/wrapper/generator execution-kind corpus |
| AC-010 | VERIFIED | SOL-001 nominal fix and SOL-003 subclass promotions; directional/hook corpus |
| AC-011 | VERIFIED | Union logic, typed Literal equality and opaque Annotated metadata corpus |
| AC-012 | PARTIALLY SATISFIED | SOL-005 still changes nominal proofs for a bare typing.Tuple destination |
| AC-013 | VERIFIED | Missing/gradual aggregation, independent uncertainty and strict/permissive corpus |
| AC-014 | VERIFIED | Module/owner resolution, requirement overlays and candidate isolation on runtime matrix |
| AC-015 | VERIFIED | Raw explicit/string/deferred annotation factory counters on runtime matrix |
| AC-016 | PARTIALLY SATISFIED | SOL-006 write proof remains incomplete when a property supplies the attribute |
| AC-017 | PARTIALLY SATISFIED | SOL-006 custom assignment dispatch can bypass a standard property setter |
| AC-018 | PARTIALLY SATISFIED | SOL-001 equality-hook execution and SOL-006 intercepted property acceptance |
| AC-019 | VERIFIED | Empty-contract dictionary bypass, result truth/completeness and blocked obligations |
| AC-020 | VERIFIED | Exact two-code permissive allowlist and accepted/validate agreement |
| AC-021 | VERIFIED | Immutable records/context and independent finite JSON diagnostics |
| AC-022 | PARTIALLY SATISFIED | SOL-004 fixed; SOL-001 class equality can still raise during known unsupported lookup |
| AC-023 | VERIFIED | Actual eight report states, independent findings and policy-specific hints |
| AC-024 | VERIFIED | SOL-007 export escaping; existing 60-column/pure-rendering corpus |
| AC-025 | VERIFIED | Identity-keyed cache, old/new/failed-refresh snapshots and candidate mutation |
| AC-026 | VERIFIED | Weak declaration/IR ownership, self-reference/failed-frame collection and namespace bypass |
| AC-027 | VERIFIED | Scalar identity keys; publication/refresh/reentrant/concurrent corpus; compilation outside lock |
| AC-028 | PARTIALLY SATISFIED | Executable docs pass, but SOL-005 contradicts advertised alias normalization |
| AC-029 | PARTIALLY SATISFIED | SOL-008 measured wide-member workload still lacks wide keyword-presence choices |
| AC-031 | VERIFIED | Full CI matrix, canonical reuse and fail-closed artifact/version/evidence validator corpus |

AC-030 is withdrawn and is not a blocker. Twenty-two active criteria are VERIFIED; eight are PARTIALLY SATISFIED. None is classified REGRESSED because the remaining defects were present before remediation rather than introduced by it.

## Previous blockers

All original verification names are in [review-01 tests](../../../tests/test_sol_review_blockers.py). Their complete run passes on every supported minor. Additional verification is in [review-02 tests](../../../tests/test_sol_review_02_blockers.py).

| Finding | Status | Verification and fix inspection |
| --- | --- | --- |
| SOL-001 | PARTIALLY FIXED | Original two checks pass. Identity-keyed weak cache, nominal routes and compiler exclusions are correct; static candidate lookup still invokes owner equality |
| SOL-002 | VERIFIED FIXED | Original check passes; explicit marker plus actual typing/typing_extensions Protocol MRO identity required |
| SOL-003 | VERIFIED FIXED | Original check passes; numeric promotions derive from MRO identity; reverse directions and subclass-hook corpus pass |
| SOL-004 | VERIFIED FIXED | Original check passes; descriptor TypeError/ValueError handled narrowly and empty contracts bypass dictionary inspection |
| SOL-005 | PARTIALLY FIXED | Original two cases pass; special-case patch still differs from the bare nominal destination for erased/nominal sources |
| SOL-006 | PARTIALLY FIXED | Original frozen-storage check passes; property writes are explicitly excluded from custom assignment uncertainty |
| SOL-007 | VERIFIED FIXED | Original check passes; evidence text fields, locations and nested context are escaped before export/rendering |
| SOL-008 | PARTIALLY FIXED | Original check passes; one mandatory keyword exists, but no signature has independent optional keyword presence decisions |
| SOL-009 | VERIFIED FIXED | Original check passes; async-generator required getters fail in members phase; supported getter and candidate uncertainty corpus passes |

## Remaining blockers

These are continuations of the original root causes, not four new findings. All new verification fails for the expected reason against both the source implementation and the canonical installed wheel on CPython 3.11–3.14.

### SOL-001 — Class identity replaced by overloaded equality and hashing

Severity: **Medium** for the remaining dispatch-boundary impact; the original high-severity cache/nominal false-certification paths are fixed.

Disposition: **BLOCKER**.

Related AC: **AC-005, AC-018, AC-022**. Original AC-004/010/025/027 portions are now verified.

Location: `src/stipulate/_compatibility.py:212`, `inspect_candidate` owner classification.

Problem: `lookup_owner in (...)` still uses class equality. A candidate with an ordinary-metadata metaclass and a custom Python __getattribute__ invokes the metaclass's __eq__ twelve times while deciding that custom lookup is unsupported.

Evidence: `test_sol_001_static_lookup_does_not_execute_class_equality` returns UNKNOWN but records twelve equality calls. A separately executed probe with a raising equality implementation makes check raise RuntimeError before producing the expected unsupported-dispatch result. Neither candidate lookup nor its method needs to execute to establish this limitation.

Relationship to current change: This identity-sensitive membership expression existed in the initial implementation and survived the identity remediation. The cache, compiler and nominal engine no longer exhibit the original examples; this remaining inspection path has the same equality-versus-identity root cause.

Why it matters: Known unsupported dispatch can execute user metadata operations and fail before an ordinary candidate diagnostic is returned.

Why this blocks the current change: AC-018 requires non-permissible uncertainty without invoking custom hooks; AC-022 requires expected lookup limitations to be diagnosed at their boundary. The original finding requires identity throughout class classification, not only cache lookup.

Required behavior: Class-owner classification preserves identity, performs no overloaded equality/hash operation, and leaves custom candidate lookup UNKNOWN and non-permissible without invoking it. Preserve the fixed cache and nominal behavior.

Acceptance criteria: The original SOL-001 checks remain green; the new dispatch check returns UNKNOWN with no equality or lookup calls. Raising class equality is never reached in this execution path.

Verification artifact: `tests/test_sol_review_02_blockers.py:test_sol_001_static_lookup_does_not_execute_class_equality`.

Verification status: **FAILS** on all four source and installed-wheel targets due to twelve equality-hook calls.

### SOL-005 — Bare typing.Tuple interpreted as a fixed empty tuple

Severity: **Medium**.

Disposition: **BLOCKER**.

Related AC: **AC-012, AC-028**.

Location: `src/stipulate/_relations.py:223–234`, `relate` route checking and bare-Tuple special cases.

Problem: The patch handles the original parameterized sources, but does not normalize the bare destination alias as the bare nominal tuple. typing.Tuple → tuple is PROVEN, while typing.Tuple → typing.Tuple is gradual UNKNOWN. An ordinary nominal tuple subclass → tuple is PROVEN, while the same source → typing.Tuple is unsupported UNKNOWN.

Evidence: `test_sol_005_bare_tuple_destination_alias_preserves_nominal_proofs` fails for both typing.Tuple and TupleSubclass. The bare builtin destination controls pass. These relations need no erased element or length information.

Relationship to current change: The original alias-normalization root cause remains. The source-is-Tuple special case and pre-special-case generic-substitution check still select different semantics for aliases of the same bare destination. These defects were present before remediation.

Why it matters: Replacing an advertised supported legacy alias with its builtin counterpart changes strict acceptance and completeness.

Why this blocks the current change: The approved type table explicitly requires alias normalization and conclusive nominal flow where no erased element information is needed. This does not request generic specialization of tuple subclasses.

Required behavior: A bare typing.Tuple destination preserves the same nominal proofs as tuple. Keep tuple[()] distinct, and retain uncertainty for erased sources when a parameterized destination actually requires length/element information.

Acceptance criteria: Both original SOL-005 cases and both new nominal/erased-source cases are conclusively compatible; existing fixed-empty, fixed-length, homogeneous and generic-subclass restrictions remain correct.

Verification artifact: `tests/test_sol_review_02_blockers.py:test_sol_005_bare_tuple_destination_alias_preserves_nominal_proofs`, two source cases.

Verification status: **Both cases FAIL** on all four source and installed-wheel targets with incomplete UNKNOWN instead of PROVEN.

### SOL-006 — Instance storage falsely certifies writable capability

Severity: **High**.

Disposition: **BLOCKER**.

Related AC: **AC-005, AC-016, AC-017, AC-018**.

Location: `src/stipulate/_compatibility.py:512`, `_attribute` custom-write condition.

Problem: The new custom-write check applies only when raw is not a property. Python assignment reaches custom __setattr__ before standard property setter dispatch. A candidate with an annotated getter/setter and __setattr__ that rejects every assignment is therefore still declared COMPATIBLE/complete for a writable value:int requirement.

Evidence: `test_sol_006_custom_assignment_dispatch_also_intercepts_property_writes` proves the read-only control remains compatible and all getter/setter/assignment counters stay zero during checks, then fails because the writable result is compatible and permissively accepted.

Relationship to current change: The original independent-write-proof defect is fixed for frozen plain storage but survives for property storage. The condition explicitly excludes this route; the false certification also existed before remediation.

Why it matters: validate can return an object certified for assignment even though its actual assignment dispatch rejects that capability.

Why this blocks the current change: Required writes need independent proof; a statically visible setter does not establish usable assignment when a custom hook intercepts it. Unsupported dispatch must never receive compatible or permissive acceptance.

Required behavior: Custom assignment interception prevents certification of required property writes unless supported behavior can be established without execution. Preserve read-only acceptance, ordinary supported properties/storage, and known mutability/type mismatches. Never probe by calling the hook or setter.

Acceptance criteria: Original SOL-006 and the new property-dispatch check pass; the writable result rejects under both policies while the read-only control passes and operation counters remain zero.

Verification artifact: `tests/test_sol_review_02_blockers.py:test_sol_006_custom_assignment_dispatch_also_intercepts_property_writes`.

Verification status: **FAILS** on all four source and installed-wheel targets with COMPATIBLE/complete writable certification.

### SOL-008 — Wide benchmark omits keyword-only call partitions

Severity: **Medium**.

Disposition: **BLOCKER**.

Related AC: **AC-029**.

Location: `tools/benchmark.py:24,80–96`; `docs/releases/0.1.0/benchmark.json`.

Problem: The revised fifty-member workload has one method with one mandatory keyword-only key. That key has exactly one legal presence subset; the signature has no independent optional keyword choices. The other forty-nine methods still have one positional-or-keyword input. This measures wide member count, but not the wide keyword-presence dimension whose potentially exponential cost motivated the explicit plan requirement.

Evidence: The original verification checks only that any wide-workload parameter is keyword-only, so it passes. The new verification inspects actual benchmark IR and finds no signature with multiple independently optional keyword-only parameters. The recorded measurement's environment, source digest and wheel hash are valid, but valid association cannot supply an omitted workload.

Relationship to current change: This continues the original benchmark-coverage omission. Adding one mandatory keyword satisfies the earlier test's minimum assertion while leaving the identified call-partition risk unmeasured. No latency defect or optimization requirement is inferred.

Why it matters: Existing measurement cannot characterize the keyword-subset cost required by the approved exact-call algorithm plan.

Why this blocks the current change: The plan explicitly requires wide keyword-only benchmarking before release, and review 01 identified the exponential call-partition dimension. The expected workload is not a new performance threshold or feature.

Required behavior: Record a representative keyword-only signature with several independent optional-keyword presence decisions; document its chosen width and retain wide-member coverage. Measure against the exact installed candidate with environment/iterations/source/artifact association and no unsupported latency claim.

Acceptance criteria: Actual benchmark IR exercises multiple independent optional keyword choices within a signature, original wide-member coverage remains, and fresh measured release evidence records the workload dimensions. The verification sets only a lower bound rejecting the current degenerate case; it does not mandate an exact width, implementation algorithm or latency target.

Verification artifact: `tests/test_sol_review_02_blockers.py:test_sol_008_wide_benchmark_has_independent_keyword_presence_choices`.

Verification status: **FAILS** on all four source and installed-wheel targets. Timing/digest/origin stubs and synthetic distribution bytes are verification-only and were not promoted into measured evidence.

## Quality gates

The implementation's [completed GitHub workflow](https://github.com/eddiethedean/stipulate/actions/runs/34733178468) passed source quality on Python 3.11–3.14, canonical build/twine, all eight clean wheel/sdist consumers, and evidence assembly. That run predates these additional review checks; its success does not override their failures.

| Gate | Actual result | Classification |
| --- | --- | --- |
| All original 171 tests on every minor | PASS | Previously correct covered behavior preserved |
| Full current source matrix | 171 passed, 5 failed per minor | EXPECTED BLOCKER VERIFICATION; every failure is in review-02 tests |
| Additional checks against canonical installed wheel on every minor | Five expected failures per minor; site-packages origin asserted | EXPECTED BLOCKER VERIFICATION |
| Existing eleven review-01 checks | PASS on every minor | Original examples remediated, broader invariants assessed separately |
| Ruff lint and final formatting | PASS | Review artifacts conform; initial formatting issue corrected before handoff |
| Strict Pyright, pinned mypy public/source gate, Markdown checks | PASS | Executed locally after adding verification |
| Wheel/sdist twine verification | PASS | Existing canonical artifacts checked without rebuilding production |
| Required local evidence assembly | PASS | Recorded association validates; not semantic release approval |
| PRE-EXISTING / UNRELATED required gate failures | None established | No follow-up scope expansion |

Source matrix: CPython 3.11.15, 3.12.13, 3.13.11 and 3.14.3; pytest 8.4.2, Hypothesis 6.140.3, typing_extensions 4.15.0. Source runs explicitly set PYTHONPATH=src; focused installed runs omit src and assert site-packages origin. JUnit artifacts are under ignored `evidence/sol-review-02/`. An initial new-test draft used int.__getattribute__, whose inheritance differs on 3.14; it was corrected to a portable custom Python lookup before final matrix verification. The final five failures have the same expected assertions on all targets, with no collection errors.

Run the complete handoff with `uv run --locked --extra dev --python 3.11 python -m pytest -q`. Focus remaining invariants with `uv run --locked --extra dev --python 3.11 python -m pytest -q tests/test_sol_review_02_blockers.py`; preserve and also rerun `tests/test_sol_review_blockers.py`.

## New blockers, follow-ups and observations

New blocker IDs: **none**. Four existing IDs remain open. No confirmed unrelated defect or observation is handed to implementation. Open GitHub issues were searched and none existed; no follow-up issue needed creation.

## Convergence

- Previous blockers resolved: **5 of 9**.
- Blockers remaining: **4**, all PARTIALLY FIXED: SOL-001, SOL-005, SOL-006, SOL-008.
- New blockers attributable to remediation: **0**.
- Follow-ups discovered: **0**.
- The loop is converging from nine blockers to four; these fixes need their invariant completed rather than a broader redesign.
- Escalation is not recommended yet: only one implementation attempt has occurred. If a blocker survives more than one attempt, apply the repeated-failure protocol.

Only these four remaining BLOCKERS enter the next Luna remediation. Production implementation remains unchanged by this review. No release tag or publication was performed.
