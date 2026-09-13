# Contract Engine

## Semantic center

The engine compares provided declarations against required declarations. Compatibility means each supported required operation is available with compatible call shape, binding, and types, assuming declarations describe actual behavior.

One normalization and relation engine powers candidate checks and eventual evolution analysis. Relation context is explicit: metadata conformance and universal contract evolution have different obligations when gradual or unknown types are involved.

## Layers

1. Compile a supported Protocol into immutable `ContractIR`.
2. Inspect a candidate into an ephemeral provided-contract view.
3. Compare capabilities and types, producing evidence.
4. Aggregate a policy-independent `CompatibilityResult`.
5. Enforce strict or permissive acceptance and return the original candidate or raise `ContractError`.

Later serialization and comparison consume the same IR and relation rules. They are not public 0.1 operations.

## Contract IR

```text
ContractIR
  declaration identity and diagnostic provenance
  members
    MethodContract: binding, legal calls, parameter types, return type, execution kind
    AttributeContract: read type, write type, storage capability
    PropertyContract: getter, optional setter
  normalized TypeExpr graph
  compilation policy and supported feature set
```

Candidate evidence and enforcement policy do not enter the requirement IR. Public `Contract[T]` is a typed facade holding one snapshot. Keep source provenance outside the semantic fields used for future serialization.

Recursive references use explicit graph identities and a cycle-aware relation context. A cache of visited pairs must distinguish pending from established relations; recursion is not unconditional compatibility. Unsupported recursive forms remain explicit until dedicated support lands.

## Evidence and aggregation

Evidence has `PROVEN`, `INCOMPATIBLE`, or `UNKNOWN` status, a stable code and location, expected/actual metadata, provenance, and an optional actionable hint. PROVEN means an obligation about declarations was established, not that a method body was executed.

Conjunctive requirements aggregate as follows:

| Findings | Result status | Truthiness | Strict acceptance | Permissive acceptance |
| --- | --- | --- | --- | --- |
| All obligations established | COMPATIBLE | True | Yes | Yes |
| At least one incompatible finding, with or without unknowns | INCOMPATIBLE | False | No | No |
| No incompatibility; unknowns only from the allowlist below | UNKNOWN | False | No | Yes |
| No incompatibility; any other unknown reason | UNKNOWN | False | No | No |

`complete` means every applicable obligation was decided. It is independent of success: a fully analyzed incompatible object is complete. Blocked dependent obligations must remain explicitly unassessed; do not manufacture completeness by dropping them. An empty valid contract is compatible and complete.

Disjunctive type relations use three-valued logic: one established branch suffices for an OR, all disproven branches disprove it, otherwise it is unknown. An AND is disproven by any failed obligation, established only when all succeed, otherwise unknown. Apply this inside union and other relation algorithms before aggregating independent member requirements.

There is no second public assurance enum or confidence score in 0.1. `status`, `complete`, and detailed evidence suffice.

## Enforcement policy

`validate(candidate, strict=True)` and `result.accepted(strict=True)` share the exact same acceptance function. `check()` never applies enforcement policy.

Permissive acceptance may tolerate only candidate type unknowns with codes `annotation_missing` and `gradual_type`. Known member presence, binding, signature, and execution-kind checks must still pass. Missing required members, unsupported types, unresolved expressions, unavailable signatures, dynamic members, and inspection failures cannot be waived by `strict=False`.

Unknowns retain their original status and provenance after acceptance. A permissive return type is a documented trust boundary comparable to adopting untyped code, not a complete metadata proof. Invalid requirements always raise `ContractDefinitionError` independently of enforcement policy.

## Exceptions

`ContractError` means a valid contract rejected the candidate under the requested policy. It includes the result and the findings responsible for rejection, including unknowns rejected by strict policy.

`ContractDefinitionError` means the requirement could not be compiled. `check()` does not swallow definition errors or unexpected internal defects. Expected candidate inspection limitations become unknown evidence; process-control exceptions propagate.

## Evolution semantics — later release

For old contract O and new contract N, under fully supported, fully static semantics:

- Implementers: O is assignable to N. Every implementation meeting O also meets N.
- Consumers: N is assignable to O. A consumer using O's operations can use N.

| Change from old to new | Existing implementers | Existing consumers |
| --- | --- | --- |
| Add a required method | Incompatible | Compatible |
| Remove a required method | Compatible | Incompatible |
| Widen accepted parameter from int to object | Incompatible | Compatible |
| Narrow returned value from object to int | Incompatible | Compatible |
| Add an optional parameter to an existing method | May be incompatible: old implementations need not accept it | Compatible if old calls and results are preserved |

These are independent perspectives, not a single “breaking” direction. Member kinds, mutability, and call shapes remain part of the analysis.

Python gradual assignability involving Any is not a universal substitutability guarantee. For example, returns `int`, `Any`, and `str` permit pairwise gradual assignments through Any without making int assignable to str. Never infer transitive evolution safety through such evidence. Use the same engine with a universal-guarantee context; return UNKNOWN wherever the guarantee depends on unsupported or gradual assumptions. Independent mismatches can still establish incompatibility.

`report.implementers` and `.consumers` are CompatibilityResults. `report.breaking` is True if either direction is INCOMPATIBLE, False only if both are COMPATIBLE, and None otherwise. `report.complete` requires both directions complete. CI fails on incompatible or unknown required directions by default. Report objects have no implicit truthiness; reject it to avoid ambiguous policy decisions. The CLI can explicitly select which direction matters.

## Canonical schema and fingerprints — later release

Versioned schema work must specify member ordering, unions, aliases, nominal type identity, generic bindings, recursive references, default presence versus default values, ignored Annotated metadata, and portability before publication.

A semantic fingerprint excludes display names, source locations, and irrelevant default values. Callable compatibility depends on default presence; changed default behavior can be reported separately but is not behavioral proof. Preserve nominal identities; never merge unrelated types merely because names match. Process-local or non-portable identities must be rejected for portable snapshots or explicitly marked non-portable, not serialized using unstable repr output.

Use an explicit format such as `stipulate-contract-v1:sha256:<digest>`. A fingerprint difference does not imply incompatibility. Loading snapshots must not automatically import or execute arbitrary type references.

## Native implementation boundary

The initial core is Python. Normalize Python inspection objects before relation analysis, but retain the runtime identity information needed for correctness. A future native core is justified only by profiling; do not constrain 0.1 around speculative Rust or force premature portable serialization.
