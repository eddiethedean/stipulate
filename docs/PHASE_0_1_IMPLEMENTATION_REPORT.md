# Phase 0.1 initial implementation report

This implements the approved [architecture contract](PHASE_0_1_IMPLEMENTATION_CONTRACT.md). It is an implementation handoff, not independent approval or a production-readiness declaration. The user withdrew AC-030; participant testing is optional and does not block release.

## Requirements and evidence map

IMPLEMENTED means runtime/tooling behavior is present and covered by the named tests. WITHDRAWN identifies a requirement removed by the user. All source paths below are repository-relative; private tools are not part of the installed public API.

| Criterion | Status | Relevant implementation | Coverage |
| --- | --- | --- | --- |
| AC-001 distributions/exports | IMPLEMENTED | pyproject.toml, MANIFEST.in, src/stipulate/__init__.py, py.typed | test_packaging_api.py; clean wheel/sdist consumers |
| AC-002 installed public typing | IMPLEMENTED | _contract.py; TypeForm constructor | typing_fixtures/public_api.py and negative.py; both pinned installed checkers |
| AC-003 eager requirement compiler | IMPLEMENTED | _compile.py | test_boundaries.py; test_contract.py; test_type_table.py |
| AC-004 inherited obligations | IMPLEMENTED | _compile.py:_satisfies | conflicting, override and diamond cases in test_boundaries.py |
| AC-005 real identity validation | IMPLEMENTED | _contract.py, _compatibility.py | test_contract.py; actual storage operations in test_reports_and_examples.py |
| AC-006 configuration/API | IMPLEMENTED | _contract.py | test_contract.py; test_reports_and_examples.py; namespace copying/isolation |
| AC-007 every legal call | IMPLEMENTED | _signatures.py exact finite partition and language binder | Hypothesis-generated independent actual Python-call oracle; targeted collision/omission/variadic regressions |
| AC-008 signature layers/binding | IMPLEMENTED | _signatures.py:exposed_signature/unbind | test_annotation_layers.py; malformed/cyclic overrides and receiver removal |
| AC-009 execution kind | IMPLEMENTED | _compile.py, _compatibility.py | coroutine/sync mismatch, visible wrapper and generator exclusions |
| AC-010 nominal/numeric relations | IMPLEMENTED | _relations.py | test_type_table.py; no subclass-hook execution |
| AC-011 union/Literal/Annotated | IMPLEMENTED | _relations.py | explicit directional truth table; malicious metadata repr counter |
| AC-012 finite collections/exclusions | IMPLEMENTED | _relations.py:supported/relate | all table routes, tuple lengths/empty tuples, invariance and malformed arities |
| AC-013 gradual/three-valued logic | IMPLEMENTED | _relations.py:all_of/any_of; _compatibility.py | Any, bare erasure, independent mismatch plus unknown, strict/permissive cases |
| AC-014 trusted resolution | IMPLEMENTED | _annotations.py | module/owner inheritance, overlays, unresolved independent return, safe expression failures |
| AC-015 raw nonevaluation | IMPLEMENTED | _annotations.py; annotation-free function cloning | eager/string/deferred/raw and explicit Signature factory-counter cases on runtime matrix |
| AC-016 storage presence | IMPLEMENTED | _compatibility.py:_instance_dict/_attribute | annotation-only absence, stored untyped values, class storage, no value inference |
| AC-017 properties | IMPLEMENTED | _compile.py, _compatibility.py:_attribute | getter/setter counters, contravariant setter names, storage satisfying readonly property |
| AC-018 dynamic/descriptor boundaries | IMPLEMENTED | static MRO/dictionary lookup | custom getattribute/getattr/metaclass, slots, class candidates, callable/static/generator exclusions |
| AC-019 results/completeness | IMPLEMENTED | CompatibilityResult; blocked obligations | empty, complete mismatch, independent uncertainty, missing method dependency roots |
| AC-020 shared enforcement | IMPLEMENTED | accepted(); validate() | precise strict/permissive rejection categories; original object identity |
| AC-021 immutable JSON diagnostics | IMPLEMENTED | _evidence.py | exact fields, frozen context, JSON encoding and independent nested export mutation |
| AC-022 exceptions/boundaries | IMPLEMENTED | _errors.py; narrow annotation/inspection boundaries | readonly fields, policy filtering, KeyboardInterrupt and injected engine-error propagation |
| AC-023 actual eight reports | IMPLEMENTED | _render.py | actual equivalents of every scenario in report_scenarios.json; status/completeness/policy assertions |
| AC-024 safe pure rendering | IMPLEMENTED | _render.py; safe Contract repr | control escaping, <=60-column lines, candidate/default/metadata repr counters |
| AC-025 mutation/refresh | IMPLEMENTED | _cache.py | retained old/new snapshots, failed refresh preservation, per-call candidate mutation |
| AC-026 weak lifetime | IMPLEMENTED | weak declaration keys and weak IR values | local self-reference, failed frames, candidates/IR collection; namespace bypass |
| AC-027 concurrency/reentrancy | IMPLEMENTED | compilation outside cache lock; publication under RLock | bounded first-use/refresh/check joins and reentrant evaluation from another thread |
| AC-028 executable docs/inventory | IMPLEMENTED | README, QUICKSTART, IMPLEMENTED_0_1; feature_inventory.json | actual documentation Python blocks execute against installed package; typing consumer fixtures |
| AC-029 recorded measurements | IMPLEMENTED | tools/benchmark.py; docs/releases/0.1.0/benchmark.json | ten workloads with exact environment, version, source digest and installed wheel association |
| AC-030 participant study | WITHDRAWN | Removed at the user’s request | Not required by the release validator; no participant observations claimed |
| AC-031 CI/release gate | IMPLEMENTED | both workflows; tools/quality, installed_check, assemble_evidence, release_evidence | validator positive/negative fixtures; canonical artifact consumers; missing/benchmark/hash/path/version/tag failures |

## Changes and architecture

The src-layout package implements all nine public exports with the invariant TypeForm API. Eager compilation validates supportedness and all inherited obligations. Static per-call inspection separates storage presence, shape, execution kind and directional type proof. Results retain independent failures and uncertainty, proven facts and blocked obligations; permissive enforcement changes acceptance only.

Signature containment uses all named positional boundaries plus the unbounded tail representative and all legal keyword-presence equivalence classes. Legal-class pruning removes impossible omissions and duplicates without sampling or a cutoff. The independent oracle exposed an inspect.Signature.bind version difference for omitted optional positional-only names passed through **kwargs; the engine uses Python language routing directly.

Trusted annotation handling resolves each available expression independently with its own module/owner and explicit requirement overlays. Raw handling uses annotation-free clones and static materialization checks, including Python 3.14's deferred class metadata. Unsupported or inaccessible forms remain explicit unknowns. Standard property and instance-dictionary metadata are inspected without operations; custom hooks/descriptors remain conservative.

The cache keeps weak keys and weak values, compiles outside its lock, reuses a concurrently published live snapshot for ordinary construction, and publishes refreshes only on success. Evidence exports recursively freeze/copy finite JSON values. Reports consume collected labels and evidence only, escape controls and wrap to 60 columns.

Development tools and transitive dependencies are locked in uv.lock; setuptools 80.9.0 is the pinned PEP 517 backend. CI separates source quality, canonical build, eight isolated installed consumers, and evidence assembly. Release downloads and verifies previously checked artifacts and never rebuilds them before OIDC publication.

## Verification

The verification artifacts record 160 tests, Ruff lint/format, strict first-party Pyright, pinned mypy TypeForm consumers, positive/negative existing design probes, Markdown checks, canonical build/twine validation, and installed positive/negative fixtures. Runtime targets are CPython 3.11–3.14 and installed consumers explicitly use typing_extensions 4.15.0. Exact patch versions and tool arguments are captured in evidence manifests rather than inferred from import success.

No PyPI publication, release tag, actual participant study, or independent Sol review was performed. Hosted GitHub execution is distinct from local execution of the same gates. Benchmark numbers describe this environment and make no latency claim.

## Remaining issues and handoff

AC-030 was withdrawn by the user. The release validator requires the other 30 criteria and retains all runtime, typing, packaging, benchmark, integrity and documentation gates. Participant research may be conducted later without blocking phase 0.1.

The documented excluded type/member forms remain intentional 0.1 limits. External mutation is a point-in-time assumption and dishonest declarations cannot be verified through metadata. The sole approved scope change is withdrawal of the participant-study requirement.

Next step: **Sol — Production Code Review**.
