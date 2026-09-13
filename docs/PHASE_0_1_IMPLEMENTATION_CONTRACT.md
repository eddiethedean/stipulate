# Phase 0.1 — Architecture and implementation contract

Planning baseline: commit `40019aa`, inspected 2026-09-12. This document plans the **entire 0.1 core-validation release** in ROADMAP.md, not only engineering Slice 1. It authorizes no production implementation or publication in this planning change.

Status: architecture ready; implementation and release evidence outstanding. REQUIRED BEHAVIOR below defines the implementation boundary. RECOMMENDED IMPLEMENTATION may be adapted internally while preserving that behavior. The [roadmap](ROADMAP.md) owns release scope, [design decisions](DESIGN_DECISIONS.md) own durable policy, and focused specifications retain their documented authority. The clarifications selected here are incorporated into the relevant focused specifications in this planning change.

## Architecture summary and repository ground truth

The checkout contains Markdown specifications, illustrative report scenarios, typing stubs, isolated Python probes, and two workflows. There is no `src/stipulate`, production API, `pyproject.toml`, package test suite, distribution, persistence layer, migration infrastructure, or public extension registry to preserve or modify. `design_probes/contract_api.py` intentionally raises on import; its stub cannot serve as the implementation.

Inspected sources include README, ROADMAP, IMPLEMENTATION_PLAN, DESIGN_DECISIONS, INTERFACE_MODEL, CONTRACT_ENGINE, TYPE_SYSTEM, VALIDATION_ENGINE, ERROR_MODEL, ARCHITECTURE, STATIC_TYPING, TESTING_STRATEGY, PERFORMANCE, DEPENDENCIES, COMPATIBILITY, EXPERIENCE_DESIGN, QUICKSTART, PRODUCT_VISION, OPEN_TECHNICAL_PROBLEMS, RELEASING, the scenario catalogue, all design probes, and both workflows. Inherited members, annotation resolution, signature normalization, and type relations are the main extension points; their normalized records remain private.

Existing CI tests design probes on CPython 3.11–3.14, positive/negative mypy on 3.11, and Markdown formatting/local links. If package metadata exists, it installs `.[dev]` and runs pytest. It **does not yet gate Ruff, production Pyright, production public typing, installed distributions, lifecycle tests, or observed usability**. `release.yml` reuses checks, verifies semantic 0.1 tags and distribution filename versions, runs twine, and publishes through the `pypi` OIDC environment. Its build intentionally fails without package metadata. Green design checks alone cannot approve a release.

Reproduced locally with CPython 3.11.14, Pyright 1.1.411, mypy 1.19.1, and typing_extensions 4.15.0: positive Pyright has zero diagnostics; positive mypy passes with `--enable-incomplete-feature=TypeForm`; negative Pyright has the expected five rules; negative mypy has six expected errors, including the rejected `type[T]` fallback; runtime ownership/evaluation probes pass. A separate CPython 3.14.3 experiment confirmed that `inspect.signature(eval_str=False)` can evaluate deferred function annotations, while signature recovery from an annotation-free function clone does not. These are planning experiments, not package acceptance results. The open GitHub issue inventory was empty at inspection.

The implementation follows this ownership and operation pipeline:

```text
Protocol -> eager compiler -> immutable, weak-referenceable ContractIR
                               ^ strongly owned by Contract[T]
                               ^ weakly referenced by global weak-key cache

candidate -> static per-call inspection -> directional relations
          -> immutable evidence -> policy-independent CompatibilityResult
          -> explicit enforcement -> original candidate or ContractError
                                 -> pure plain-text presenter
```

## Change boundary

**Problem:** applications loading implementations dynamically cannot establish the promised Protocol declaration compatibility or get precise, typed, actionable diagnostics from this repository today.

**Desired outcome:** an installed Stipulate package accepts an existing supported Protocol, checks a live instance without executing its operations, returns that same instance as the Protocol type when enforcement accepts it, and distinguishes a disproven requirement from insufficient metadata.

**In scope:** reproducible pure-Python packaging; the public Contract/result/evidence/error API; explicit Protocol composition and inherited-obligation validation; ordinary bound methods and coroutine methods; every ordinary Python parameter kind; the finite type table below; declared storage and standard properties; trusted/raw requirement and candidate annotation handling; explicit requirement namespaces; strict/permissive enforcement; immutable diagnostics; snapshot refresh and weak-cache concurrency/lifecycle; readable reports; installed-package examples/checker fixtures; runtime matrix, benchmarks, and fail-closed release checks.

**Touched surface:** new `pyproject.toml`, development tool lock/configuration, `src/stipulate/`, `tests/`, typing consumer fixtures, benchmark/evidence utilities, `.gitignore`, both workflows, and the existing focused documentation/examples. Internal module names follow ARCHITECTURE.md. This planning change touches documentation only. No database, data migration, service, network API, or persistent contract format is introduced.

**Explicit non-scope:** Interface shorthand; adapters/free-function validator APIs; general user generics/TypeVars; PEP 695 alias evaluation; nested Protocol types; overloads, Self, Callable annotations and advanced callable packs; generators/async generators; class/static methods; class-object preflight; arbitrary callable objects; custom descriptors/cached_property/dynamic storage support; recursive value checks; candidate coercion/wrapping; schema/fingerprint/comparison; snapshots/CLI; Pydantic; native code; hosted UI; automatic invalidation; candidate caching; public handler registration. Explicitly diagnosing such constructs is in scope; implementing their semantics is not.

## Public contract — required behavior

### API and configuration

The public exports are `Contract`, `CompatibilityResult`, `CompatibilityStatus`, `Evidence`, `EvidenceStatus`, `DiagnosticRecord`, `StipulateError`, `ContractError`, and `ContractDefinitionError`. Use this constructor/method shape; `T` is invariant and tied to the declaration by TypeForm:

```python
class Contract(Generic[T]):
    def __init__(
        self, declaration: TypeForm[T], *,
        annotations: Literal["trusted", "raw"] = "trusted",
        globalns: Mapping[str, object] | None = None,
        localns: Mapping[str, object] | None = None,
        refresh: bool = False,
    ) -> None: ...
    def validate(self, candidate: object, *, strict: bool = True) -> T: ...
    def check(self, candidate: object) -> CompatibilityResult: ...
    @property
    def contract(self) -> Contract[T]: ...
```

This is a contract sketch, not runnable implementation. `.contract is self`. No persistent strictness setting, `check(strict=...)`, implicit declaration coercion, checker plugin, consumer ignore, or public Any escape is allowed. Static TypeForm accepts more expressions than the runtime compiler; it does not promise validation of non-Protocols. `Contract(Storage)` infers `Contract[Storage]`; both validate modes return `Storage` statically. `Contract[int](Storage)` is rejected by the supported checkers.

Reject non-bool `strict`/`refresh` with TypeError, including integers; non-string `annotations` with TypeError; unknown annotation-policy strings with ValueError; and non-mapping namespaces or non-string namespace keys with TypeError. Validate configuration before compilation/checking; ordinary Python argument-binding errors retain their standard behavior. Namespace bindings are shallow-copied. No environment variables or configuration file affect semantic outcomes.

Any supported instance may be a candidate, including `None` or primitives; missing capabilities are reported normally. A class object produces non-permissible `unsupported_candidate` uncertainty, including for an empty contract, without construction. An ordinary object satisfies an empty valid Protocol with COMPATIBLE/complete=True and no evidence. Additional candidate members are ignored.

### Requirements and inheritance

Accept actual non-generic Protocol declarations, from typing or the tested typing_extensions equivalent, with or without runtime_checkable. Reject normal classes (including subclasses missing the explicit Protocol marker), non-Protocol type forms, malformed supported member declarations, and unsupported requirement forms eagerly with ContractDefinitionError. A Protocol root is an empty declaration. A generic declaration or specialization is unsupported even if a broad runtime signature seems inspectable.

Discover the Protocol's declared members under its annotation policy, including explicit single/multiple Protocol inheritance. Framework/typing bookkeeping and constructors are excluded according to standard Protocol member-discovery rules; declared private names and supported special methods must not be dropped merely for starting with an underscore. Never read metadata through a user metaclass hook to obtain a false certainty.

For every member collect all inherited obligations. Diamond copies of the same declaration are deduplicated. An explicit override must conclusively satisfy each inherited obligation using the same capability/call/type directions used for candidate checks; an UNKNOWN override proof is insufficient. Without an override, an effective inherited declaration must conclusively satisfy every base's obligation. Otherwise raise `conflicting_member`; do not silently rely on favorable MRO order. Inherited read-only/writable capabilities remain distinct. Unsupported or absent required parameter/return annotations (except the receiver) fail construction; explicit Any is valid gradual intent. Required property getter returns and setter value parameters must be annotated; a standard setter return is `None`.

### Supported types and directions

Normalize and validate supportedness before reflexive/identity fast paths. `rel(S, D)` means values declared as S may be supplied where D is required. Parameters require `rel(required_input, provided_input)` for **every possible argument route**; returns and reads require `rel(provided_output, required_output)`; writes require `rel(required_write, provided_write)`.

| Supported form | Required rule |
| --- | --- |
| Ordinary nominal classes, None/NoneType | Preserve class identity; use declared nominal inheritance, with int→float→complex typing promotions and int→complex. bool retains its nominal relationship to int. Do not execute custom subclass/instance hooks to decide relations. |
| `Union` and `A \| B` | Each source branch must fit the destination; a destination alternative suffices when conclusively established. Branch ordering has no semantic effect. |
| `Literal` | Legal typing Literal values (int/bool/str/bytes/None/enum members), flattened; equality requires both value type and value identity/equality within those safe kinds. A literal may flow to its supported base nominal type; a broad nominal type cannot establish a literal restriction. |
| `Annotated[T, ...]` | Compare underlying T only. Retain opaque metadata internally without invoking its repr or enforcing constraints. |
| `Any`, bare supported containers | UNKNOWN `gradual_type` exactly when the relation relies on wildcard/erased arguments. A relation independently established against object may be conclusive. Required Any is not rewritten to object. |
| Legacy alias assigned to a supported expression | Same relation as the resolved expression; unavailable names follow annotation policy. |

The finite parameterized-origin table is authoritative for 0.1:

| Source | Supported destination routes |
| --- | --- |
| `list[T]` | list invariant; Sequence and Iterable covariant in T |
| `set[T]` | set invariant; Iterable covariant in T |
| `dict[K, V]` | dict invariant in both; Mapping invariant in K/covariant in V; Iterable covariant in K |
| fixed `tuple[T1, ... , Tn]`, including `tuple[()]` | Same-length fixed tuple elementwise covariance; `tuple[T, ...]`, Sequence, Iterable if every element fits T |
| homogeneous `tuple[T, ...]` | Homogeneous tuple, Sequence, Iterable covariant in T; cannot establish a fixed length |
| `Sequence[T]` | Sequence and Iterable covariant in T |
| `Mapping[K, V]` | Mapping invariant in K/covariant in V; Iterable covariant in K |
| `Iterable[T]` | Iterable covariant in T |
| nominal `str`, `bytes`, `bytearray` | Sequence/Iterable of str, int, int respectively |

Normalize typing aliases for these collection origins to their collections.abc/builtin counterpart. A parameterized container also flows to its own bare nominal origin, documented nominal bases, or object without using erased element types when none are required. There is no additional parameterized-origin substitution, including arbitrary generic subclasses. Unsupported destination/source type syntax cannot be waived just because the opposite side is object or Any. Wrong generic arity, nested Protocols, recursive alias expansion, unbound TypeVars, ClassVar/Final wrappers, and all excluded typing constructs fail required normalization or produce `unsupported_type` candidate uncertainty. Guard normalization cycles and never evaluate newer alias objects simply to expand the advertised table.

For three-valued relations, AND fails on any disproven branch and succeeds only if all succeed; OR succeeds on one established branch and fails only if all fail. Otherwise retain UNKNOWN. Discard unknown alternatives that were unnecessary to a successful OR; retain independent unknown obligations alongside a disproven AND. Invariance checks both directions without pretending Any-mediated assignability is transitive.

### Methods, binding, and call shapes

Support ordinary Python instance methods exposed by standard descriptor binding. Remove the receiver once, including for inherited methods and externally exposed signatures. A missing/unbindable receiver in a requirement is a definition error. Candidate binding that is custom or unsupported is an explicit unknown, not guessed from a parameter named self.

A candidate must accept every legal required call: positional-only, positional-or-keyword with both permitted routes, keyword-only, omission of defaults, extra candidate required parameters, `*args`, `**kwargs`, and positional/keyword duplicate-binding collisions. Defaults matter by presence, never arbitrary value comparison or repr. Variadic annotations denote individual argument types. Prove shape containment deterministically; do not call the candidate, generate user values, or approximate by a fixed collection of sample calls.

Recover a well-formed non-None explicit `__signature__` first, then the supported `__wrapped__` chain, then the visible Python function. A malformed non-None override or wrapper cycle stops recovery with candidate `signature_unavailable`; it cannot be hidden by falling back to a different signature. Unsupported requirement recovery is a definition error. Selected exposed parameter/return annotations and their defining owner/module supply the declaration and provenance; do not merge inconsistent layers. Unknown signature/binding blocks dependent type obligations, but independent members and known execution-kind mismatches are still analyzed.

0.1 requires matching ordinary def/coroutine async def execution kinds in both directions. A synchronous wrapper returning Awaitable does not establish an async def declaration. The visible callable supplies execution kind; a wrapped coroutine alone cannot certify its synchronous wrapper. For coroutine functions compare the annotated awaited result directly, without adding a second coroutine wrapper. Generators, async generators, and callable objects remain unsupported. Exposed signatures are trusted declarations about behavior, not execution proofs. This is an explicit runtime policy beyond ordinary static callable assignment.

### Annotations and trust boundaries

Use the selected policy consistently for requirement compilation and candidate inspection. Trusted mode resolves eager/string/deferred annotations with version-appropriate facilities and preserves Annotated extras. It may execute annotation expressions. Do not automatically import unavailable or TYPE_CHECKING-only names. Resolve per member where possible so one unresolvable return does not suppress an independent known parameter mismatch.

Each selected callable/attribute declaration uses its **own** defining module globals and declaring owner locals, with inherited owner context preserved. For requirements, supplied globalns entries overlay defining globals and localns entries overlay owner locals; explicit locals have ordinary local lookup precedence. Candidate resolution never receives the constructor namespace mappings. Objects referenced by copied mappings are not deeply frozen. Unavailable function-local names need explicit requirement mappings or yield candidate uncertainty.

Raw mode never requests string/ForwardRef evaluation or invokes deferred annotation functions, including STRING/FORWARDREF formats. On 3.14, do not access a deferred `__annotations__` getter or call ordinary inspect.signature on an annotation-bearing function merely with eval_str=False. If a non-evaluating route cannot obtain a required annotation or even the required member set, raise `annotation_unresolved` in the definition phase. On candidates, record non-permissible `annotation_unresolved` and any dependent unassessed obligations. Already materialized annotation dictionaries and explicit Signature metadata containing actual supported types may be used where obtainable without invoking a factory. Raw is therefore deliberately narrower on deferred declarations and does not undo evaluation performed during import or by other callers.

Catch ordinary annotation-expression exceptions only at the exact resolution boundary: requirement failures become definition diagnostics; candidate failures become `annotation_unresolved` with safe metadata. Expected inspect TypeError/ValueError or known lookup limitations get their documented unknown code. Do not catch the whole engine, cache failures/tracebacks, suppress internal bugs, or intercept BaseException/process-control/cancellation exceptions. Neither annotation mode is a sandbox; do not claim validation of untrusted plugins is safe.

### Storage, properties, and dynamic uncertainty

A bare declared attribute is readable and writable. Require separately established storage presence and declared read/write type relations. Supported storage is an initialized entry in an ordinary instance dictionary or a plain class dictionary entry supplying an instance-accessible attribute, with annotations on the declaring class/MRO. A plain class entry supplies writable instance capability only where ordinary instance dictionary storage permits shadowing it; a statically read-only storage layout cannot satisfy a writable requirement. An annotation alone is not storage. An uninitialized annotation-only member is `missing_member` when ordinary lookup makes absence conclusive; a stored but unannotated value is present with `annotation_missing` type evidence. Never infer a declaration from that value's runtime type.

A standard property supplies the getter return read type and, if present, setter value write type, without calling either. A read-only property cannot satisfy a writable requirement. Plain storage may satisfy a read-only property if its declared read relation passes. Incompatible mutability uses `member_kind`; wrong read/write annotations use `attribute_type` or `property_type` with the capability in the location. No getter, setter, deleter, or descriptor is invoked to establish storage or types. Standard slots remain explicitly uncertain (`descriptor_unverifiable`) when initialization cannot be established without calling their descriptor; document this 0.1 limitation rather than inspecting the descriptor value.

Custom descriptors, callable values with custom binding, cached_property, proxies, and custom `__getattribute__` that can intercept required members produce non-permissible uncertainty. With ordinary `__getattribute__` and custom `__getattr__`, a statically present supported member can be checked; an absent member is `dynamic_member_unverifiable` without calling the hook. Custom metaclass lookup that would be needed to collect trustworthy metadata likewise remains unsupported. Dynamic hooks do not turn known static absence into a compatible declaration. The empty contract has no member lookup obligations.

### Results, evidence, errors, and serialization

CompatibilityStatus has uppercase Python members with values `compatible`, `incompatible`, `unknown`; EvidenceStatus has `proven`, `incompatible`, `unknown`. CompatibilityResult exposes read-only `status: CompatibilityStatus`, `compatible: bool`, `complete: bool`, and `evidence: tuple[Evidence, ...]`; `bool(result)` equals compatible. Evidence exposes read-only `loc: tuple[str | int, ...]`, `status: EvidenceStatus`, `code: str`, `msg: str`, `expected: str | None`, `actual: str | None`, `source: str`, `hint: str | None`, and `ctx: Mapping[str, object]`; nested context is recursively immutable. User construction of engine records and IR is not a public contract.

Any incompatible independent finding makes the result INCOMPATIBLE. Otherwise any needed unknown makes it UNKNOWN; all established obligations yield COMPATIBLE. `complete` is false if any applicable obligation is unknown/unassessed, including dependent ones. A missing method has one incompatible presence root and explicitly UNKNOWN `dependency_unassessed` facts for its blocked obligations, so it is incomplete. A fully inspected type mismatch can be complete. Failed union alternatives do not count as independent required obligations.

`errors()` and `unknowns()` return fresh lists of fresh JSON-compatible DiagnosticRecord dictionaries, with recursively independent nested loc/ctx values. Every record has exactly the documented fields `loc`, `type`, `status`, `msg`, `expected`, `actual`, `source`, `hint`, `ctx`; unavailable expected/actual/hint are null. No live type/value/namespace objects, exception repr, non-finite floats, or arbitrary metadata enter these records. Dependency-unassessed facts are included in unknowns(), with a root location reference in ctx; the presenter groups them without changing structured counts. Full public fields/codes are those in ERROR_MODEL.md; PROVEN facts use the code for the established capability/relation.

`accepted(*, strict: bool = True)` and validate share one enforcement function. Strict accepts only COMPATIBLE; permissive accepts COMPATIBLE or UNKNOWN containing **only** `annotation_missing` and `gradual_type`, after known presence/binding/shape/kind obligations pass. Incompatible findings and every other unknown always reject. Policy selection does not mutate evidence, status, completeness, or truthiness.

StipulateError derives from Exception. ContractError exposes read-only `.result`, `.strict`, and `.errors()` containing findings responsible for rejection: incompatible findings under either policy; all unknowns in strict mode; non-allowlisted unknowns in permissive mode. Returned dictionaries are independent copies. ContractDefinitionError exposes read-only `.code`, `.loc`, `.phase`, `.msg`, and `.hint`; phase is one of declaration/members/annotations/types/inheritance, code follows ERROR_MODEL.md, and no candidate result exists. It may report the first deterministic definition failure; multi-definition-error aggregation is not required. `check()` never raises ContractError for expected candidate outcomes.

Order members lexicographically, then presence/kind/signature, parameters in declaration order, return, read, write, and blocked obligations. Stable metadata source labels are `declaration`, `signature`, `annotation`, `inspection`; ctx may refine the selected signature/annotation source. Deduplicate the same routed type obligation; preserve independent failures. For mismatched routed arguments use the required parameter location and record the provided route in ctx; return/read/write locations end in return/read/write.

### Presentation

str(result), repr(result), repr(contract), and exception strings consume collected evidence/safe labels only. No second check, implicit policy, logging, candidate repr/str, or arbitrary metadata repr occurs. Use the result headlines and compact repr forms from EXPERIENCE_DESIGN.md; a definition error starts “Cannot compile <name>”. Exception text adds the requested policy and rejected findings. Exact prose may improve; codes/categories and required/provided directions may not.

Show every actionable mismatch and primary unknown, aggregate blocked dependents visibly, and identify an empty contract with “No required members”. Suggest strict=False only for allowlisted type uncertainty. A symbolic required-call counterexample may be included in ctx only if established by the deterministic shape proof. Escape terminal/control characters in all labels/source text before export/rendering. Default text targets 80 columns; test the same private presenter at 60. Long identifiers can wrap with continuation indentation while exported labels remain complete. Core text has no ANSI, Rich dependency, value dumps, namespace dumps, or silent truncation.

### Snapshots, cache, lifecycle, and concurrency

Contract strongly owns one immutable IR; weak-cache keys and values must not strongly retain declarations directly or indirectly. CompilationKey contains scalar interpretation-policy values, excludes strictness and refresh, and never captures types/namespaces/IR. Supplying either namespace mapping, even an empty one, bypasses shared caching.

Retained contracts keep their normalized snapshots after requirement mutation. Ordinary construction may reuse a live cached snapshot; it need not detect mutation. `refresh=True` recompiles current requirements and atomically publishes only a successful new snapshot; failure leaves the prior cache entry and all retained contracts usable. If no live owner remains, cached IR may expire and ordinary construction may recompile. Snapshot immutability covers normalized declarations/bindings, not deep freezing of external class objects or imported dependencies; those mutations need refresh and are documented assumptions.

Lookup/publication use a small lock; compilation, annotation evaluation, relations, and candidate inspection run outside it. Duplicate first-use compilation is allowed; ordinary publication reuses an already live entry. Concurrent successful refreshes use completion/publication order (last publication wins); overlapping ordinary construction may see either valid snapshot. Cache reuse/identity and exactly-once annotation evaluation are not public guarantees. No failed compilation, candidate result/object, or traceback is globally cached. Every check re-inspects current candidate metadata. Concurrent checks have independent evidence; simultaneous external candidate/declaration mutation has no atomic observation guarantee and requires caller synchronization.

## Recommended implementation and invariants

Use the private modules in ARCHITECTURE.md, frozen dataclasses/tuples and immutable context, a weak-referenceable IR, and small typed wrappers around interpreter-specific inspection. Prefer inline public annotations plus py.typed; stubs are permitted only with runtime agreement checks. A final cast to T is appropriate **after** acceptance, never as the validation engine.

Use standard-library primitives and typing_extensions as the only initial runtime dependency. Set requires-python >=3.11. Select setuptools with its PEP 517 backend for a pure-Python src-layout build; pin the tested backend in build-system requirements. Start testing typing_extensions==4.15.0 and declare >=4.15.0 only after its matrix passes. Preserve Pyright 1.1.411 and mypy 1.19.1/TypeForm flag initially. Pin pytest, Hypothesis, Ruff, build, twine, and build-backend versions in a committed reproducible development lock after validating them; selecting compatible tool patch versions does not change semantics. No unpinned “latest” tool output may be the release evidence.

For deterministic call containment, use exact symbolic binding partitions, not random/sample testing. One concrete baseline algorithm is:

1. Let B be the maximum named positional capacity of the two normalized signatures. Partition positional counts into 0..B and an unbounded tail represented by B+1; the tail is relevant only when the requirement accepts it. Beyond B, named routing is stable and additional positions route solely to variadic parameters.
2. Let K contain both signatures' named parameter spellings, including positional-only spellings that may enter **kwargs. Partition keyword presence into subsets of K plus one fresh spelling outside K. Multiple fresh spellings are equivalent for shape/type routing because ordinary **kwargs has one homogeneous value type and no cardinality constraint.
3. Bind each symbolic partition to the requirement, discard its illegal partitions, and prove each legal partition binds to the candidate. Binding operates on inert tokens/Signature metadata, never candidate functions. Candidate duplicate-binding or omission failures establish a shape mismatch.
4. For all legal partitions collect required-to-provided argument routes, compare their types, and compare return/kind independently. Record an established symbolic failure when useful. Prove tail/fresh-name equivalence in algorithm documentation and tests so finite representation is an exhaustive partition of infinite call sets.

This exhaustive approach can be exponential in keyword names. Prune impossible partitions and memoize normalized route obligations; an equivalent symbolic constraint algorithm is permitted with the same independent proof corpus. Do not introduce a cutoff that silently certifies compatibility. Benchmarks must include wide keyword-only contracts before release.

For raw shape recovery on plain functions, an annotation-free temporary FunctionType clone sharing code/globals/defaults/closure, without executing it or retaining it globally, is one viable way to recover unannotated input shape. Follow signature/wrapper precedence explicitly and resolve annotations separately. Version adapters must distinguish a stored annotations mapping from a deferred getter/factory; blindly using get_annotations or get_protocol_members is insufficient for raw mode.

The executable invariants are: immutable per-result evidence; no candidate operations during checks/reports; no unsupported reflexive success; every legal required route checked; UNKNOWN never promoted by policy; fail-closed non-allowlisted uncertainty; independent status/completeness; separate namespaces; no strong global ownership cycle; no failed refresh publication; no mutable candidate state in IR/cache; pure presentation; original-object identity on acceptance. There is no auth/authorization/transaction subsystem in this local library. Trust boundaries are annotation evaluation and deliberate permissive adoption of missing/gradual types.

## Acceptance criteria and verification matrix

Every row is a required, observable release criterion. Proof paths below are proposed implementation tests, not files or results already present. “Matrix” means all advertised CPython 3.11–3.14 targets. Installed consumer checks run from a temporary directory/environment without repository import paths, for the wheel and a wheel rebuilt from the sdist separately.

| ID | Observable acceptance criterion | Preferred proof | OTP |
| --- | --- | --- | --- |
| AC-001 | Wheel and sdist install, export the nine public names and py.typed, and report matching package/metadata versions with Python >=3.11 and the tested runtime dependency. | Integration/static: distribution contents, clean matrix installs, import/metadata checks | 025 |
| AC-002 | Installed valid consumers infer Contract[Storage] and Storage returns; invalid explicit T, invalid structural assignments/return use, and invalid policies produce the expected checker codes without consumer suppressions. | Contract/compatibility: pinned Pyright strict and mypy TypeForm fixtures for each artifact and matrix target | 010, 026 |
| AC-003 | Supported Protocols construct eagerly; normal classes, implicit-marker subclasses, non-Protocol forms, malformed/unsupported requirements and absent required annotations raise located definition errors before candidate inspection. | Unit/contract: test_compile.py plus negative definition corpus | 013 |
| AC-004 | Explicit inheritance/composition preserves every obligation; valid overrides/diamonds succeed and inconclusive/conflicting overrides fail deterministically with conflicting_member. | Unit/compatibility: test_inheritance.py and checker fixtures | 004, 010, 013 |
| AC-005 | Compatible validation returns the identical original object silently; a known mismatch rejects in both modes; check returns evidence without ContractError. | Integration: quickstart and test_contract.py with identity/output assertions | 013, 026, 028 |
| AC-006 | All specified input argument errors occur before work; .contract is self; check has no strict argument; candidates need no framework relationship and extras are ignored. | Contract: test_public_api.py, counters, signature/static assertions | 026 |
| AC-007 | A candidate accepts all required positional/keyword/default/variadic routes or receives a located shape mismatch, including extra required arguments and name collisions. | Unit/property: test_signatures.py; independent bounded Signature.bind oracle and tail/collision cases | 003 |
| AC-008 | Standard/inherited method binding is normalized once; exposed signatures and wrapped chains obey precedence; malformed overrides/cycles yield non-permissible unknown or a definition error. | Unit/integration: test_signature_sources.py with distinct layer annotations and hook counters | 015 |
| AC-009 | Def/coroutine mismatches fail in both directions; matching coroutine result types compare once; generators/callable objects and misleading wrappers remain explicitly unsupported. | Unit/compatibility: test_execution_kind.py, never executing functions | 016 |
| AC-010 | Nominal contravariant inputs/covariant outputs, None, and numeric promotions produce the declared directional outcomes without custom subclass hooks. | Unit/property/contract: specification-indexed test_nominal.py and side-effect counters | 004, 010 |
| AC-011 | Union ordering is irrelevant; Literal[True] differs from Literal[1]; literal/base directions and Annotated underlying types follow the finite rules without executing metadata repr. | Unit/property: test_special_types.py and independent three-valued relation cases | 004 |
| AC-012 | Every route in the collection table obeys its variance/length rules; omitted args remain gradual; malformed and unlisted origins never pass identity or wildcard shortcuts. | Unit/contract: table-indexed test_collections.py with positive/negative/unknown/definition cases | 004, 028 |
| AC-013 | Missing and Any-dependent candidate types are UNKNOWN; object is not substituted for Any; a conclusive OR can succeed without unused unknown branches and mixed independent mismatch/unknown remains incomplete INCOMPATIBLE. | Unit/property: test_relation_logic.py, test_gradual.py | 004, 028 |
| AC-014 | Trusted eager/string/deferred types resolve under each declaration's owner/module and explicit requirement overlays; TYPE_CHECKING/unavailable names fail in the proper boundary without arbitrary imports. | Matrix integration: cross-module/local/deferred annotation fixtures and effect/import counters | 005, 013, 025 |
| AC-015 | Raw mode does not invoke annotation factories or string/ForwardRef evaluation through signature/member discovery; unavailable required/candidate metadata yields the specified definition/unknown outcomes. | Matrix integration: test_raw_annotations.py, including 3.14 deferred and materialized metadata | 005, 025 |
| AC-016 | Declared plain storage requires presence and read/write assignability; annotation-only absence fails, a matching current value cannot hide a mismatched declaration, and an unannotated stored value remains type-unknown. | Unit/integration: test_storage.py with differing runtime value/declaration | 011, 012 |
| AC-017 | Standard properties and plain storage satisfy only their supported read/write obligations; read-only implementations reject writable requirements; getter/setter/deleter counters stay zero. | Unit/integration: test_properties.py | 012 |
| AC-018 | Dynamic lookup, custom descriptors/dispatch, uninspectable slots and class-object candidates produce the specified non-permissible uncertainty without invoking hooks or constructing instances. | Unit/integration: test_inspection_limits.py with counters and strict/permissive decisions | 011, 014 |
| AC-019 | Status, truthiness, completeness, empty-contract behavior, independent failures and blocked obligations match the defined aggregation rules. | Unit/contract: exhaustive result truth table in test_results.py | 028 |
| AC-020 | accepted defaults to strict and agrees with validate for every result; permissive tolerance is exactly the two-code allowlist and never mutates findings/status. | Unit/property/integration: test_enforcement.py across codes and mixed findings | 028 |
| AC-021 | Result/evidence fields and nested context cannot be mutated; exported diagnostics have all specified JSON-safe fields and independent nested copies with deterministic codes/locations/order. | Unit/contract: test_evidence.py, JSON encoding and mutation isolation | 022 |
| AC-022 | Both exception paths expose the defined attributes; rejection errors include precisely the policy-rejected categories; expected inspection failures become unknown and internal/BaseException failures propagate. | Unit/fault injection: test_errors.py and narrow boundary cases | 013, 022 |
| AC-023 | Result/exception reports cover all eight scenario states, preserve required/provided directions, show empty/blocked obligations, have accurate counts, and offer permissive hints only for allowlisted uncertainty. | Integration/contract: actual engine equivalents of report_scenarios.json; semantic assertions independent of text snapshots | 022, 029 |
| AC-024 | str/repr are deterministic plain text, readable at 60/80 columns, escape control metadata, retain full actionable findings, and make no candidate/metadata repr calls or hidden writes. | Unit/integration/manual: test_render.py with long/malicious labels, counters, snapshot review | 029 |
| AC-025 | Retained old/new contracts keep separate normalized snapshots; successful refresh observes requirement mutation; failed refresh preserves the old cache; subsequent checks observe candidate mutation. | Integration: test_refresh.py and candidate monkey-patching | 020 |
| AC-026 | Dead local/self-referential declarations, IR, candidates and failed-resolution frames are collectable after owners are released; live Contracts retain usable IR; custom namespaces bypass shared caching. | Lifecycle integration: weakrefs, forced GC, test_cache_lifecycle.py | 021 |
| AC-027 | Concurrent first use, refresh and repeated checks publish only valid immutable snapshots, share no mutable evidence, and finish without deadlock; evaluation is not performed under a cache lock. | Integration: barrier-controlled test_cache_concurrency.py, reentrant evaluation and bounded joins | 021 |
| AC-028 | Real installed quickstart/README examples execute and type-check; every advertised feature maps to runtime/checker cases and limitations remain explicitly labeled. | Matrix integration/static: executable documentation fixtures, link checks and feature inventory | 010, 025, 026, 029 |
| AC-029 | Recorded baselines distinguish cold compile, retained/temporary construction, inspection, compatible/incompatible/unknown checks, enforcement, wide contracts and supported type depth, with exact environment and no unsupported latency claim. | Benchmark evidence/manual review; no correctness timing threshold | 024 |
| AC-030 | Withdrawn at the user’s request: participant research is optional and does not block phase 0.1. | Excluded from required evidence IDs; remaining IDs are preserved | 029 |
| AC-031 | CI gates pytest, Ruff, production Pyright strict, pinned mypy consumers, installed distributions, existing probes and docs on the required matrix; release validation additionally refuses a missing/incomplete evidence bundle and mismatched artifact/tag metadata. | Static/integration: workflow review, reusable checks, release-validator failure/success fixtures, metadata extracted from wheel and sdist | 010, 025 |

## Dependency-aware implementation phases

These phases refine the existing engineering slices inside release 0.1; they do not rename the roadmap's later releases. Each phase includes useful failure/uncertainty examples. Intermediate work must not be advertised as the entire supported release.

| Phase | Goal and modules | Required behavior and proof | Documentation/configuration work | Dependencies |
| --- | --- | --- | --- | --- |
| P1 — typed installation | src layout, __init__, _contract public shape, _typing_compat; packaging/tooling | AC-001/002 foundation, AC-006 signatures; installed wheel and sdist consumer inference/negative diagnostics, matrix imports. Runtime operations may explicitly raise NotImplementedError temporarily; no fake successful validation. | pyproject/dev lock/py.typed/.gitignore, strict configs, CI installed consumers; retain planned-status labels | None |
| P2 — first real validation | _ir, _compile, _members, _annotations, _assignability, _compatibility, _evidence, _errors, _render | Nominal single-method path, original identity, incompatible parameter, missing candidate return, invalid/empty definition, strict/permissive truth table; AC-003/005/019–023 narrow cases, AC-022 boundaries | Execute first quickstart; document narrow intermediate subset; add structured/public type tests | P1 |
| P3 — every legal call | _signatures, _members, _typing_compat, _render | AC-007–009, complete binding/shape algorithm and proof, source precedence/cycles, execution kind, blocked dependent evidence and independent failures | Callable specification-indexed corpus, real call-shape report; no migration | P2 |
| P4 — finite type/annotation matrix | _assignability, _annotations, _compile, _typing_compat | AC-010–015, collection table, gradual/union logic, eager/string/deferred/raw policies and unsupported cycle termination; finish inherited-obligation AC-004 against full relations | Type table and namespace/raw caveats; cross-module fixtures and checker-policy comparison register | P3 |
| P5 — storage/capabilities | _members, _compile, _assignability | AC-016–018, getter-free properties, presence/type separation, dynamic dispatch and slot/class-object limitations | Executable storage/property examples; supported inventory; no value-validation claims | P4 |
| P6 — retained reuse/reliability | _cache, _ir, _contract; candidate paths | AC-025–027 and first AC-029 baselines; weak-key/value lifetime, explicit namespace bypass, refresh failure/races, reentrancy and independent candidate state | Snapshot/mutation/ownership guide; benchmark environment/results; cache tests | P4; P5 before full member lifecycle run |
| P7 — beta experience | _render, public docs/examples, evidence tooling | Complete AC-021–024/028–029; real scenario catalogue, 60/80-column review, installed example runs and focused fixes/retests | Remove planned labels only for implemented/proven features; record exact support/checker matrix and limitations | P5 and P6 |
| P8 — release decision | workflows, release validator, metadata/evidence artifact | AC-031; rerun final matrix on exact candidate artifacts, trace all ACs to evidence and verify metadata versions; no unresolved attributable blocker | Release evidence index/version, supported feature inventory, benchmark records, RELEASING instructions | All previous phases and every AC |

No phase requires a persistence migration. Avoid a monolithic placeholder API implementation; P2 must actually inspect and enforce before P3 expands declarations. Internal normalization/type handlers can evolve within this contract without adding public future-release operations.

## Compatibility, risks, and failure modes

Preserve the recorded TypeForm behavior, explicit structural composition, strict default, identity return, truthiness/allowlist, annotation trust policy, evidence export shape, and cache snapshot policy. There are no released Stipulate APIs or persisted user data in this checkout to migrate; do not treat historical prototypes as compatibility authority. Keep design probes as regression evidence alongside production fixtures. Support CPython 3.11–3.14 only after the full advertised matrix passes; PyPy and future interpreter features are not implied support.

Key risks are deterministic callable partition complexity, version-specific deferred annotation/member discovery, misleading wrapper metadata, arbitrary nominal metaclass hooks, unsupported dynamic storage, Any-dependent partial evidence, and indirect retention through normalized graphs/errors. Address them with the dedicated ACs, typed adapters, independent test oracles, and measured wide-contract cases. External concurrent mutation and dishonest annotations remain documented assumptions, not guarantees to implement. No automated timeout or sandbox around arbitrary annotation expressions is promised; cancellation/process-control exceptions must propagate.

Missing input is an ordinary argument error; an invalid declaration is a definition failure; an ordinary missing candidate capability is incompatible with blocked evidence; missing/gradual candidate types are optionally tolerable unknowns; unsupported/unresolved metadata remains non-permissible. Known mismatch plus unknown still rejects and remains incomplete. Repeated check never reuses candidate success. Repeated refresh publishes successful new snapshots only. Failed resolution/refresh must not poison a previous snapshot or cache an exception.

The release evidence bundle is a machine-validated index of AC IDs, exact feature inventory, source revision/artifact hashes, runtime/checker/tool versions and flags, automated verification results, benchmark measurements, documentation runs, and remaining limitations. A claimed passing row requires a referenced artifact; missing/unrun/failed rows block release. A validator proves bundle completeness and artifact association. Preserve existing 0.1 tag restrictions/OIDC environment; no publish operation occurs during implementation without a release request.

### Release evidence gate — implementation contract

Use a private JSON evidence format (not a public contract schema or API). The generated bundle contains `evidence.json` with required fields: `format_version: 1`, `release_version` (exact 0.1 patch), `source_revision` (checked-out SHA), `runtime_source_digest` (SHA-256), `distributions` (wheel/sdist relative paths and SHA-256s), `tools` (names, exact versions and argument arrays), `supported_features` and `excluded_features` (named rows matching the tables above), `matrix` (one passing entry per 3.11–3.14 target with exact patch/checker versions), `criteria` (exactly one row per active AC-001..029 and AC-031; AC-030 is withdrawn), and `limitations` (documented excluded behavior only). A criterion row has `id`, `state: "passed"`, and a nonempty `proofs` array; each proof has `kind` (automated/manual/benchmark), bundle-relative artifact path and SHA-256. The validator rejects duplicate/missing IDs, non-passing states, missing/hash-mismatched artifacts, paths escaping the bundle, mismatched versions/digests, or unsupported claimed features.

Store benchmark inputs under `docs/releases/<version>/` with their tested version, runtime-source digest, installed distribution hash, environment, tasks/cases and measured results. AC-030 is withdrawn and participant records are not required. AC-029 must include measurements for every listed workload, without a speed threshold. Compute the runtime-source digest deterministically over sorted tracked `src/stipulate` files, pyproject/development lock/configuration, README, and all docs except `docs/releases/`: hash path + NUL + file-content SHA-256 + newline for each entry, then hash the resulting sequence. The evidence directory is excluded to avoid a self-referential digest. Measurements may precede their evidence commit/tag if this digest and release version match the final candidate; changed runtime or instructional content requires new corresponding measurements.

Restructure reusable checks into source quality, one canonical distribution build on 3.11, installed wheel/sdist matrix checks against those artifacts, and final evidence validation. The final job assembles/upload checks' exact distributions and evidence. Release's build/verify job downloads those artifacts and validates tag plus **embedded** wheel METADATA/sdist PKG-INFO versions and hashes, without rebuilding them; publish downloads that verified set. Ordinary PR checks run all automated gates and report missing benchmark evidence. A nonempty release_phase requires the complete passing bundle, including benchmark evidence; missing evidence blocks publication. Do not extend the current editable-install-only checks and assume they establish the distribution boundary.

### Semantic references

The implementation corpus records specific sections from the primary [callable specification](https://typing.python.org/en/latest/spec/callables.html#assignability-rules-for-callables), [Protocol specification](https://typing.python.org/en/latest/spec/protocol.html), [TypeForm specification](https://typing.python.org/en/latest/spec/type-forms.html), [gradual type concepts](https://typing.python.org/en/latest/spec/concepts.html), and [Literal specification](https://typing.python.org/en/latest/spec/literal.html). The runtime adapter also follows the documented [annotationlib evaluation effects](https://docs.python.org/3.14/library/annotationlib.html#security-implications-of-introspecting-annotations) and [inspect signature behavior](https://docs.python.org/3.14/library/inspect.html#inspect.signature). These sources guide the bounded implementation; the additional strict-evidence, storage, and execution-kind requirements remain explicit Stipulate policies.

## Known pre-existing problems and follow-up candidates

- Absent implementation/distribution tests and incomplete production CI are **in-scope foundation work**, not unrelated bugs to waive at release. The current release metadata failure is intentional.
- Historical “Phase 2/3/4/5/6” labels in deferred OTP entries are older engineering-stage terminology. ROADMAP's 0.3/0.4/0.5/0.6/0.7 mapping controls their release targets; relabeling the historical register is a documentation follow-up and does not pull those features into 0.1.
- General descriptor/slot support, nested protocols, generic specialization, advanced callables, portable schemas/evolution and candidate caching remain the already registered later gates. Broader 0.2 hardening cannot be used to defer a required 0.1 AC silently.
- No unrelated production defect was confirmed: production code does not exist. No new GitHub follow-up issue is warranted from speculation. If implementation identifies an unrelated defect, search for a duplicate and file/reference a focused issue; it blocks this change only if it makes the bounded implementation unsafe or impossible.

## Definition of done

This change is ready to release only when all 30 active criteria (AC-001 through AC-029 and AC-031) have demonstrable evidence, required compatibility and all relevant existing/new gates pass, documentation matches the installed candidate, and no substantive regression or release blocker attributable to this scope remains. Independently confirmed pre-existing failures may be identified separately; they do not excuse missing in-scope package gates. Do not mark OTPs resolved from this plan or these design experiments. Record resolution only against checked-in implementation tests and the passing advertised matrix.

The repository need not be globally defect-free. Unknown later constructs remain explicitly unsupported. Scope changes require an explicit roadmap/specification/AC revision, never a silent fallback or weakening of strictness.

READY FOR IMPLEMENTATION
