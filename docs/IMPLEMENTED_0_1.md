# Implemented 0.1 feature guide

Stipulate 0.1 compares declarations at the boundary where an application accepts an implementation. It returns the original object on acceptance. It does not run candidate methods, getters, setters, lookup hooks, or custom descriptors to establish compatibility. Trusted annotation expressions may run Python code. Neither annotation policy is a sandbox.

## Public API

`Contract(ProtocolClass, *, annotations="trusted", globalns=None, localns=None, refresh=False)` eagerly compiles an actual non-generic Protocol. `.contract` returns the same Contract. `check(candidate)` returns an immutable CompatibilityResult. `validate(candidate, *, strict=True)` returns the candidate with its inferred Protocol type or raises ContractError. `check` has no strict argument; enforcement policy does not change evidence.

Results expose status, compatible, complete, evidence, errors(), unknowns(), accepted(strict=True), bool, str and repr. The status values are compatible/incompatible/unknown. Evidence statuses are proven/incompatible/unknown. All diagnostic fields are present, unavailable fields are null, and exported dictionaries are independent JSON-safe copies. An enforcement exception's errors() includes exactly the findings rejected by its policy.

Strict mode requires established compatibility. Permissive mode tolerates only annotation_missing and gradual_type, after structure and execution kind are established. Unknowns involving unresolved names, unsupported forms, descriptors, or signatures always reject. Known failure plus independent uncertainty rejects and remains incomplete. Missing members include explicit dependent unknowns.

## Supported declarations

Explicit Protocol inheritance preserves every base obligation, deduplicates diamonds, and rejects conflicting or inconclusively justified overrides. Ordinary instance methods and coroutine methods support positional-only, positional-or-keyword, keyword-only, default omission, *args and **kwargs. The visible def/async def kind must match. Signatures use a well-formed explicit __signature__, then a supported __wrapped__ chain, then the visible function; malformed overrides and cycles stop recovery.

The [finite type table](PHASE_0_1_IMPLEMENTATION_CONTRACT.md#supported-types-and-directions) covers nominal inheritance, numeric promotion, None, unions, legal Literals, Annotated's underlying type, Any, list/set/dict, fixed and homogeneous tuples, Sequence, Mapping and Iterable. Mutable containers and mapping keys are invariant. Inputs and writes are contravariant; outputs and reads are covariant. Unsupported forms are checked before identity/object/Any shortcuts.

Bare attributes need initialized ordinary instance storage or a plain class value plus a declared class/MRO annotation. Class annotations alone do not establish presence, and stored values do not supply type declarations. Bare attributes are writable, so both directions are checked. Standard properties use getter and optional setter declarations without execution. Plain storage can satisfy a read-only property. Slots and custom descriptors remain explicitly uncertain.

## Annotation policies and snapshots

Trusted mode resolves each available expression with its defining module and owner. Requirement namespaces overlay those defaults and are shallow-copied; candidates never receive them. TYPE_CHECKING-only imports are not loaded automatically. Ordinary expression failures become annotation_unresolved; process-control exceptions and unexpected engine errors propagate.

Raw mode never evaluates strings, ForwardRefs, or deferred factories. An annotation-free function clone recovers call shape. On Python 3.14 a deferred function's materialization cannot be detected through a safe public getter, so raw mode conservatively reports annotation_unresolved unless an explicit Signature supplies actual types. Classes can use materialized annotation caches available in their static dictionary. This policy does not reverse evaluation already performed at import or by another caller.

Retain Contracts for repeated use. A live Contract owns its immutable snapshot; the shared cache has weak declaration keys and weak snapshot values. Namespace mappings, including empty ones, bypass it. refresh=True atomically publishes a successfully compiled new snapshot; failure preserves the previous one. Old Contracts retain their previous snapshot. Candidates are inspected on every call. External concurrent mutation does not promise an atomic view.

## Development and verification

Use `uv sync --locked --extra dev --python 3.11`, then `uv run --locked --extra dev python -m tools.quality`. uv.lock pins the complete development dependency graph. Runtime depends only on typing_extensions >=4.15.0; installed consumers test that minimum. The build backend is setuptools 80.9.0, and TypeForm consumer fixtures use Pyright 1.1.411 strict and mypy 1.19.1 with --enable-incomplete-feature=TypeForm.

The clean consumer harness runs the full suite and both checkers outside the repository against the built wheel or a wheel built from its sdist. The [feature inventory](../tools/feature_inventory.json) is machine-checked by release validation. Tests are indexed in the implementation report; no excluded feature is silently claimed as implemented.

General generics, nested Protocol types, overloads, Self, Callable annotations, PEP 695 aliases, class/static methods, generators, class candidates, custom descriptors, slots, dynamic storage, adapters, Interface, schemas, fingerprints, comparisons and value validation are excluded from 0.1. Excluded candidate declarations produce non-permissible uncertainty; excluded requirements fail eagerly. See the [release process](RELEASING.md) for evidence and independent review requirements.
