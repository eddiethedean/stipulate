# Sol production review 01

Verdict: **NEEDS FIXES**.

Reviewed implementation: `68e6d688eacf6f1b28c9c50f4e9af5b39ccda0c6`, compared with the approved architecture baseline `e63d923`. The user explicitly withdrew AC-030. The other 30 criteria remain in scope. No earlier Sol review or stable blocker IDs were found in the repository or open issue inventory.

The change introduces the first production implementation; there is no released package or persistent data to migrate. Scope includes Protocol compilation, static candidate inspection, the finite type table, immutable evidence, refresh/weak ownership, typing, packaging, executable documentation, benchmarks and release gates. General generics, nested Protocols, adapters, arbitrary descriptors, generators, class candidates, schemas, hosted UI and candidate caching remain excluded. Excluded constructs must still be diagnosed safely.

Production implementation and the approved contract were not modified. The only review changes are this report and [blocker verification](../../../tests/test_sol_review_blockers.py).

## Acceptance criteria

VERIFIED refers to the bounded criterion, not repository-wide correctness. PARTIALLY SATISFIED means existing positive coverage passes but the cited blocker violates required behavior. No criterion is classified REGRESSED against a previously working production implementation.

| AC | Status | Evidence or blocker |
| --- | --- | --- |
| AC-001 | VERIFIED | Canonical wheel/sdist, nine exports, py.typed, metadata and eight clean CI consumers |
| AC-002 | VERIFIED | Installed pinned positive/negative Pyright and mypy fixtures on all targets |
| AC-003 | PARTIALLY SATISFIED | SOL-002, SOL-009: invalid requirements can compile |
| AC-004 | PARTIALLY SATISFIED | SOL-001: equality-sensitive owner exclusions and nominal proofs cannot preserve every inherited obligation |
| AC-005 | PARTIALLY SATISFIED | SOL-001, SOL-006: unsupported/mismatching capabilities can receive compatible acceptance |
| AC-006 | VERIFIED | Configuration-before-work, exact booleans, namespace copies, .contract identity and extras |
| AC-007 | VERIFIED | Exact call partition; independent actual Python-call oracle; collision/default/tail regressions |
| AC-008 | VERIFIED | Receiver normalization, explicit/wrapped precedence, malformed metadata and cycles |
| AC-009 | PARTIALLY SATISFIED | SOL-009: generator exclusion is incomplete for required property getters |
| AC-010 | PARTIALLY SATISFIED | SOL-001, SOL-003: nominal identity and numeric-subclass promotions |
| AC-011 | VERIFIED | Union/gradual aggregation, legal Literal distinctions and opaque Annotated metadata |
| AC-012 | PARTIALLY SATISFIED | SOL-005: bare typing.Tuple is confused with a fixed empty tuple |
| AC-013 | VERIFIED | Independent mismatch plus uncertainty, successful OR pruning and two-code gradual policy |
| AC-014 | VERIFIED | Trusted per-expression module/owner resolution, overlays, candidate isolation and narrow exceptions |
| AC-015 | VERIFIED | Raw explicit/string/deferred factory counters across 3.11–3.14 |
| AC-016 | PARTIALLY SATISFIED | SOL-004, SOL-006: inaccessible dictionaries and unproved writable storage |
| AC-017 | PARTIALLY SATISFIED | SOL-006, SOL-009: write dispatch and getter execution kind |
| AC-018 | PARTIALLY SATISFIED | SOL-004, SOL-006: unsupported inspection/write dispatch does not consistently remain uncertainty |
| AC-019 | PARTIALLY SATISFIED | Aggregation passes; SOL-004 also crashes empty-contract checks although no dictionary lookup is required |
| AC-020 | VERIFIED | accepted/validate agreement and strict/permissive rejection filtering |
| AC-021 | VERIFIED | Read-only records, recursively immutable context and independent finite JSON exports |
| AC-022 | PARTIALLY SATISFIED | SOL-004: expected descriptor TypeError escapes check |
| AC-023 | VERIFIED | Eight actual scenario equivalents, accurate structured counts and policy-specific hints |
| AC-024 | PARTIALLY SATISFIED | SOL-007: exported labels retain controls although plain-text rendering escapes them |
| AC-025 | PARTIALLY SATISFIED | SOL-001: cache identity collision selects another declaration's retained snapshot |
| AC-026 | VERIFIED | Weak keys/values, self-reference/failed-frame collection and namespace bypass |
| AC-027 | PARTIALLY SATISFIED | SOL-001: weak-key lookup/publication invokes user class hashing/equality while holding the cache lock |
| AC-028 | PARTIALLY SATISFIED | Examples execute; SOL-003/SOL-005 contradict the advertised nominal/alias boundary |
| AC-029 | PARTIALLY SATISFIED | SOL-008: measured wide-member case omits the explicitly required wide keyword-only case |
| AC-031 | VERIFIED | Actual CI matrix, canonical reuse, fail-closed evidence/hash/path/version tests and OIDC verification boundary |

AC-030 is withdrawn, excluded from required evidence IDs, and is not a blocker. Participant observations are neither required nor claimed.

## Previous blockers

None. No implementation remediation attempt has occurred in this review loop.

## New blockers

Every finding below is attributable to the newly introduced implementation and violates the approved phase 0.1 contract. All executable checks are in tests/test_sol_review_blockers.py. Test names contain the stable SOL ID. They constrain required outcomes without selecting a production implementation strategy.

### SOL-001 — Class identity replaced by overloaded equality and hashing

**Severity:** High. **Disposition:** BLOCKER. **Related AC:** AC-004, AC-005, AC-010, AC-025, AC-027.

**Location:** src/stipulate/_cache.py:get_or_compile (lines 30–44); src/stipulate/_relations.py:_nominal (lines 135–150); src/stipulate/_compile.py:_compile_contract owner exclusions.

**Problem / root cause:** Class keys and membership tests use value equality/hash semantics. WeakKeyDictionary equates distinct weak declaration keys according to their metaclass operators; nominal membership tests also invoke overloaded equality.

**Evidence:** Two real Protocols, First.first and Second.second, have a standard-lookup metaclass whose class equality/hash agree. Retaining Contract(First) makes ordinary Contract(Second) reuse First's IR and accept a candidate missing second. Refreshing Second compiles the correct rejecting snapshot. Separately, an unrelated return class whose metaclass equality returns True is treated as assignable to float and executes its equality hook. Owner exclusions have the same identity-sensitive comparison pattern. Cache comparisons execute inside its lock.

**Relationship / why it matters:** This change introduces both mechanisms. They can certify a missing capability or an unrelated declared type, with complete=True.

**Why this blocks the current change:** Required declaration identity, nominal identity, inherited obligations and snapshot selection are correctness guarantees. A cache hit must never change which contract is enforced.

**Required behavior / acceptance criteria:** Preserve actual class identity throughout cache selection, member discovery and nominal proofs. User equality/hash must not manufacture compatibility or introduce arbitrary metadata evaluation under the cache lock. Distinct valid Protocol declarations enforce their own requirements; unrelated return types reject without equality-hook execution.

**Verification artifact:** test_sol_001_cache_distinguishes_equal_protocol_class_objects; test_sol_001_nominal_proof_preserves_identity_without_metaclass_equality.

**Verification status:** FAILS for expected reasons on all four targets: wrong cached compatible result and one equality-hook call.

### SOL-002 — A private marker authenticates an unrelated normal class

**Severity:** Medium. **Disposition:** BLOCKER. **Related AC:** AC-003.

**Location:** src/stipulate/_compile.py:_compile_contract, declaration marker check.

**Problem / evidence:** A normal class with _is_protocol=True and an ordinary annotated method compiles successfully despite lacking a Protocol relationship. The compiler checks the marker without establishing an actual Protocol declaration.

**Relationship / why it matters:** Introduced by this compiler; the runtime declaration boundary accepts a class outside the approved API.

**Why this blocks the current change:** AC-003 explicitly requires normal classes and non-Protocol forms to fail eagerly. A private attribute cannot substitute for the actual supported declaration form.

**Required behavior / acceptance criteria:** Reject the unrelated normal class with located invalid_contract in the declaration phase; retain support for actual typing and typing_extensions Protocol roots and explicit inheritance.

**Verification artifact:** test_sol_002_private_marker_does_not_make_a_normal_class_a_protocol.

**Verification status:** FAILS on all targets because no ContractDefinitionError is raised.

### SOL-003 — Numeric promotions stop at exact built-in classes

**Severity:** Medium. **Disposition:** BLOCKER. **Related AC:** AC-010, AC-028.

**Location:** src/stipulate/_relations.py:_nominal, lines 135–138.

**Problem / evidence:** SmallInt(int) cannot flow to float, and SmallFloat(float) cannot flow to complex. Exact source-class checks omit inherited numeric promotion routes. The pinned mypy accepts the corresponding SmallInt assignments to float and complex.

**Relationship / why it matters:** Introduced by the finite relation engine; supported nominal subclasses are rejected contrary to the declared numeric directions. The primary [numeric annotation specification](https://typing.python.org/en/latest/spec/special-types.html#special-cases-for-float-and-complex) supplies the shortcut; applying it to nominal subclasses follows the approved inheritance requirement.

**Why this blocks the current change:** Nominal inheritance and numeric promotions are advertised in-scope behavior, not general generic specialization or a proposed expansion.

**Required behavior / acceptance criteria:** Established subclasses of the supported numeric source classes inherit the documented promotion routes. Preserve directionality, avoiding reverse promotion and custom subclass/equality hooks.

**Verification artifact:** test_sol_003_numeric_promotions_include_nominal_subclasses.

**Verification status:** FAILS on all targets with a complete incompatible result for SmallInt → float; the second route remains in the same verification contract.

### SOL-004 — Inapplicable dictionary descriptor escapes as TypeError

**Severity:** Medium. **Disposition:** BLOCKER. **Related AC:** AC-016, AC-018, AC-019, AC-022.

**Location:** src/stipulate/_compatibility.py:_instance_dict, line 183.

**Problem / evidence:** Assigning Other.__dict__['__dict__'] to Candidate.__dict__ leaves a genuine GetSetDescriptorType belonging to another class. check(Candidate()) invokes it and raises TypeError because its receiver is inapplicable. Descriptor type alone does not establish a safe instance-dictionary route.

**Relationship / why it matters:** Introduced by static inspection; expected inaccessible metadata crashes inspection instead of producing an ordinary candidate outcome.

**Why this blocks the current change:** Expected inspection limitations must become non-permissible uncertainty at the narrow boundary. The contract explicitly separates these from unexpected internal errors, which must still propagate.

**Required behavior / acceptance criteria:** For a nonempty contract, return an explicit non-permissible UNKNOWN result for this unsupported dictionary route without executing arbitrary descriptors or inferring hidden storage. An empty contract must remain compatible without requiring dictionary inspection. Avoid broad engine exception suppression.

**Verification artifact:** test_sol_004_foreign_instance_dictionary_descriptor_is_an_inspection_limit.

**Verification status:** FAILS on all targets with the expected descriptor TypeError at _instance_dict.

### SOL-005 — Bare typing.Tuple interpreted as a fixed empty tuple

**Severity:** Medium. **Disposition:** BLOCKER. **Related AC:** AC-012, AC-028.

**Location:** src/stipulate/_relations.py:relate, lines 208–225.

**Problem / evidence:** Both tuple[int] → typing.Tuple and tuple[int, ...] → typing.Tuple return INCOMPATIBLE, while the corresponding destination tuple succeeds. Empty destination arguments are treated as fixed zero length without distinguishing the bare legacy alias.

**Relationship / why it matters:** Introduced by tuple normalization. The approved table requires alias normalization and conclusive parameterized-to-bare-origin flow. The [historical typing specification](https://typing.python.org/en/latest/spec/historical.html) also identifies tuple and typing.Tuple as equivalent aliases.

**Why this blocks the current change:** A supported alias changes the result of an advertised type relation.

**Required behavior / acceptance criteria:** Bare typing.Tuple must behave as the bare tuple destination; preserve the distinct fixed-empty tuple[()] form and uncertainty for erased sources when element/length information is required.

**Verification artifact:** test_sol_005_bare_typing_tuple_is_not_a_fixed_empty_tuple, fixed and homogeneous cases.

**Verification status:** Both cases FAIL on all targets with complete incompatible return evidence.

### SOL-006 — Instance storage falsely certifies writable capability

**Severity:** High. **Disposition:** BLOCKER. **Related AC:** AC-005, AC-016, AC-017, AC-018.

**Location:** src/stipulate/_compatibility.py:_attribute, line 472; inspect_candidate dispatch checks.

**Problem / evidence:** A frozen dataclass with value:int is accepted as compatible/complete for a writable Protocol value:int. Its ordinary instance dictionary exists, but its custom __setattr__ rejects assignment. The engine equates dictionary presence with established write capability and checks only read dispatch.

**Relationship / why it matters:** Introduced by storage inspection. Validation promises a capability that immediately fails when callers assign the attribute.

**Why this blocks the current change:** Writes need independent proof, and unsupported dynamic dispatch cannot be permissively accepted. Readability alone does not satisfy writable requirements.

**Required behavior / acceptance criteria:** Keep supported read-only acceptance for this candidate. For required writes, custom write interception must prevent compatible or permissive acceptance unless its capability is conclusively supported without execution. No setter/hook call may be used as a probe.

**Verification artifact:** test_sol_006_frozen_storage_does_not_prove_writable_capability.

**Verification status:** FAILS on all targets because the writable result is COMPATIBLE; the read-only control passes.

### SOL-007 — Structured diagnostic labels retain terminal controls

**Severity:** Medium. **Disposition:** BLOCKER. **Related AC:** AC-024.

**Location:** src/stipulate/_compatibility.py:_fact; src/stipulate/_relations.py:type_label; src/stipulate/_evidence.py:diagnostic.

**Problem / evidence:** A type renamed to Bad + ESC[31m + newline + Label appears unchanged in errors()[0]['actual']. Rendering str(result) escapes these characters, but exported labels do not. JSON encoding legality does not itself sanitize the decoded label.

**Relationship / why it matters:** Introduced by the evidence path; downstream diagnostic consumers can receive control-bearing metadata despite the required safety boundary.

**Why this blocks the current change:** The presentation contract explicitly requires escaping labels before both export and rendering.

**Required behavior / acceptance criteria:** Engine-produced structured labels preserve readable identity while containing no raw control characters; apply the same rule consistently to relevant expected/actual/location/source labels without invoking arbitrary repr.

**Verification artifact:** test_sol_007_exported_type_labels_escape_control_characters.

**Verification status:** FAILS on all targets because actual contains raw ESC and newline.

### SOL-008 — Wide benchmark omits keyword-only call partitions

**Severity:** Medium. **Disposition:** BLOCKER. **Related AC:** AC-029.

**Location:** tools/benchmark.py:run, lines 76–88; docs/releases/0.1.0/benchmark.json.

**Problem / evidence:** The sole wide workload repeats a one-positional-parameter method 50 times. None of its signatures has keyword-only parameters. It measures member count rather than the explicitly required wide keyword-only dimension of the exponential call partition.

**Relationship / why it matters:** Introduced evidence tooling omits an identified in-scope verification risk. No latency defect or optimization requirement is inferred from this omission.

**Why this blocks the current change:** The approved contract explicitly states that benchmarks must include wide keyword-only contracts before release; existing measurements cannot establish that requirement.

**Required behavior / acceptance criteria:** Record a documented wide keyword-only workload against the exact installed candidate, with environment, iterations and artifact/source association. Keep wide-member coverage and make no unsupported latency threshold claim. Synthetic verification inputs must never be promoted into measured release evidence.

**Verification artifact:** test_sol_008_wide_benchmark_exercises_keyword_only_partition probes actual benchmark-constructed IR; only origin/digest/timing guards are stubbed.

**Verification status:** FAILS on all targets because no wide workload includes a keyword-only parameter.

### SOL-009 — Required async-generator property getter compiles

**Severity:** High. **Disposition:** BLOCKER. **Related AC:** AC-003, AC-009, AC-017.

**Location:** src/stipulate/_compile.py:_member property getter guard, lines 119–124.

**Problem / evidence:** A Protocol property declared with async def value(self) -> int and yield 1 compiles successfully and accepts plain int storage. The getter guard excludes coroutines and synchronous generators but omits async generators, while the candidate-side getter guard includes them.

**Relationship / why it matters:** Introduced by required-member compilation; a visibly excluded execution form is normalized as an ordinary readable int property.

**Why this blocks the current change:** Unsupported required forms must fail eagerly, and generators/async generators are explicit non-scope whose safe diagnosis remains required.

**Required behavior / acceptance criteria:** Raise located invalid_contract in the members phase before candidate inspection for an async-generator property getter. Preserve supported ordinary getter behavior and existing candidate-side uncertainty.

**Verification artifact:** test_sol_009_async_generator_property_requirement_fails_eagerly.

**Verification status:** FAILS on all targets because construction raises no definition error.

## Quality gates and verification results

The reviewed implementation's [GitHub run](https://github.com/eddiethedean/stipulate/actions/runs/34731862844) passed source quality on all four minors, the canonical build/twine check, all eight installed consumers and complete evidence assembly. Independently rerun local 3.11 quality passed pytest, Ruff, format, strict first-party Pyright, pinned mypy, positive/negative design probes and Markdown. Wheel/sdist twine verification passed.

After adding review verification, each target produced **160 passed, 11 failed, 0 collection/runtime errors outside the expected test failures**: CPython 3.11.15, 3.12.13, 3.13.11 and 3.14.3, with pytest 8.4.2, Hypothesis 6.140.3 and typing_extensions 4.15.0. Every failed test name starts test_sol_. All eleven failures were inspected and match the blocker contracts. The source matrix uses PYTHONPATH=src and isolated environments; it is not presented as a new installed-distribution run. The unchanged production wheel/sdist retain the previously passing installed matrix evidence.

Run the current verification with `uv run --locked --extra dev --python 3.11 python -m pytest -q`. The focused handoff is `uv run --locked --extra dev --python 3.11 python -m pytest -q tests/test_sol_review_blockers.py`. Repeat across advertised minors after remediation. Machine-readable local results are under ignored evidence/sol-review/, including per-target JUnit XML and logs.

| Gate result | Classification |
| --- | --- |
| Original 160 tests on each minor | Passing |
| Eleven new blocker checks on each minor | EXPECTED BLOCKER VERIFICATION |
| Ruff lint/format and strict Pyright after final verification edits | Passing |
| Pinned mypy/design probes/docs on reviewed production baseline | Passing |
| Canonical package metadata and prior installed matrix | Passing |
| Existing local evidence index after reviewer reran quality | Temporarily stale generated log hashes; reassembly passes, not an implementation defect |
| PRE-EXISTING / UNRELATED required failures | None established |

A complete evidence index proves recorded gate coverage and association, not that the existing semantic corpus can find every defect. Passing earlier CI does not override the new reproducible in-scope failures.

## Follow-ups and observations

No confirmed unrelated defect warrants a GitHub issue. Open issues were searched; none existed. No follow-up or observation is handed to implementation. Historical baseline language and intentional later-release limits are not new implementation requirements.

## Convergence and handoff

- Previous blockers resolved: 0; none existed.
- Blockers remaining: 9 stable root causes, SOL-001 through SOL-009.
- New blockers attributable to remediation: 0; no remediation has occurred.
- Follow-ups discovered: 0.
- Convergence: initial bounded handoff; convergence cannot be assessed until the first remediation. No repeated-failure escalation is warranted.

Only these nine BLOCKERS enter the implementation loop. Fix production separately, preserve IDs and verification, rerun the advertised gates, record fresh benchmark evidence, and return for Sol re-review. Do not waive numeric/alias/write/inspection guarantees or reintroduce AC-030. No publication or release tag was performed.
