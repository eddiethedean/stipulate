# Architecture

## Overview

```text
Protocol declaration
  -> Contract[T] facade
  -> controlled annotation resolution and member compiler
  -> immutable ContractIR snapshot
  -> candidate inspection (per call)
  -> shared capability/type relation engine
  -> Evidence + CompatibilityResult
  -> explicit enforcement policy
  -> original candidate or ContractError
```

Compilation failures use `ContractDefinitionError`. Inspection does not execute candidate methods or getters. Default trusted annotation evaluation may execute annotation expressions; see VALIDATION_ENGINE.md.

## Public boundary

The 0.1 entry point is `Contract(ProtocolType)`. Its constructor accepts `TypeForm[T]`, preserves T through validation, and performs a runtime supported-declaration check. A normal class, union, or arbitrary type form is not automatically a valid requirement.

`Contract` exposes `validate()`, `check()`, and `.contract` identity. Later `schema()`, `fingerprint()`, and `compare()` are release-gated. Experimental Interface class-side methods delegate to Contract and never become protocol instance members.

## Internal modules

```text
src/stipulate/
    __init__.py
    _contract.py        public typed facade
    _compile.py         requirement compilation
    _ir.py              immutable normalized records
    _members.py         static member classification
    _signatures.py      binding and legal call relations
    _assignability.py   directional type relations
    _annotations.py     trusted/raw annotation policies
    _compatibility.py   result aggregation and enforcement
    _evidence.py        immutable findings
    _errors.py          public exceptions
    _render.py          pure plain-text result/exception presentation
    _cache.py           weak compilation cache
    _typing_compat.py   isolated version-specific typing behavior
```

Keep the experimental `_interface.py` bridge separate from release-critical code until accepted.

## Data ownership

The Contract facade strongly owns its immutable IR. The IR may strongly retain the declaration and type objects when needed to preserve identity and diagnostics. The global compilation cache must not strongly own that IR; both keys and cached IR values are weak references. See PERFORMANCE.md for lifecycle and race rules.

Do not attach a globally owned adapter that closes the weak-reference lifecycle through an indirect path. Do not cache candidates or successful results globally.

## Requirement versus candidate

The requirement compiler has no candidate-specific state. Candidate inspection creates an ephemeral provided view with its own resolution context and evidence provenance. Expected limitations are represented as unknown facts. A current attribute value cannot substitute for a missing declared writable type.

Read-only capabilities compare covariantly. Writable capabilities add contravariant write obligations. Methods compare every legal call shape, then argument/return relations. Execution-kind requirements are an explicit Stipulate policy, not inferred from textual return annotations alone.

## Configuration boundaries

Annotation policy and namespace identity affect compilation and cache reuse. Strictness affects enforcement only. Mutating configuration after compilation is unsupported; create a new Contract snapshot instead.

Do not hold cache locks while evaluating annotations, inspecting candidate code, or comparing types. Concurrent duplicate compilation is acceptable when publication is safe and diagnostics are deterministic. Annotation evaluation must not be advertised as exactly-once under concurrency.

## Presentation boundary

The presenter accepts normalized evidence and sanitized display metadata. It produces text without invoking candidate code, checking compatibility again, or selecting a policy implicitly. Result str/repr and exception strings share this implementation. Later terminal or browser views may style the same facts; no view is permitted to promote UNKNOWN to compatible.

## Extension rule

New types and member forms add normalized representation and relation handlers with conformance tests. They must preserve unknown evidence and share rules with future evolution analysis. A public extension/plugin framework is deferred until internal semantics stabilize.
