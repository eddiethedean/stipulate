# Error Model

## Exceptions

```text
StipulateError
├── ContractDefinitionError
└── ContractError
```

Both exception paths exist in 0.1. Do not defer definition errors or use the superseded InterfaceValidationError name.

`ContractDefinitionError` describes an invalid, unresolvable, or unsupported requirement, including the definition phase and declaration location. It can arise during Contract construction or an explicit refresh.

`ContractError` means a valid requirement rejected a candidate under the requested enforcement policy. It exposes `.result`, `.strict`, and `.errors()` containing the findings responsible for rejection. In strict mode these can include unknowns; their evidence status remains UNKNOWN rather than being relabeled incompatible.

`CompatibilityResult.errors()` contains incompatible findings only; `.unknowns()` contains unknown findings only. This distinction must be explicit in docstrings because an enforcement exception can include both categories.

## Structured findings

Use immutable Evidence records internally. `.errors()` and `.unknowns()` return newly allocated JSON-compatible `DiagnosticRecord` TypedDict records so callers cannot mutate the underlying result.

```python
{
    "loc": ["read", "key"],
    "type": "parameter_type",
    "status": "incompatible",
    "msg": "Implementation parameter does not accept the contract's str inputs",
    "expected": "str",
    "actual": "bytes",
    "source": "annotation",
    "hint": "Accept str or a compatible broader type",
    "ctx": {},
}
```

Evidence locations are tuples internally and arrays in JSON-compatible exports. Enum members are uppercase in Python and serialize to lowercase strings. Expected/actual fields use stable type rendering; preserve live type objects only in internal provenance, never raw arbitrary objects in exported data. All shown keys are present. Unavailable expected/actual/hint fields use null, loc is an array of string/integer components, and ctx is a JSON-compatible dictionary (empty when unused). This fixes one export shape rather than leaving null-versus-omission ambiguous.

## Codes

Initial incompatible codes include missing_member, member_kind, signature, parameter_kind, parameter_required, parameter_type, return_type, async_mismatch, attribute_type, and property_type.

Initial unknown codes include annotation_missing, gradual_type, annotation_unresolved, unsupported_type, signature_unavailable, dynamic_member_unverifiable, descriptor_unverifiable, inspection_failed, dependency_unassessed, and unsupported_candidate.

Only annotation_missing and gradual_type can be tolerated by permissive enforcement. Context and phase distinguish unsupported requirement definitions from unsupported candidate declarations; the latter do not prove incompatibility.

Definition codes include invalid_contract, annotation_unresolved, unsupported_type, and conflicting_member. These are distinct from candidate result statuses.

## Human experience

Errors lead with the contract name and number of actionable findings. Each finding identifies the member, explains the failed relation, and suggests a repair where a reliable suggestion exists. Do not prescribe behavioral changes inferred solely from annotations.

```text
Cannot establish compatibility with Storage

read.return
  The contract requires bytes | None, but the implementation has no return annotation.
  Add a return annotation, or explicitly allow missing type information with strict=False.
  [annotation_missing; unknown]
```

Only suggest strict=False for allowlisted type uncertainty. Unsupported signatures or types should suggest a supported declaration or explicit annotation repair instead.

## Aggregation and ordering

Collect independent failures. Order members deterministically, then callable parameters in declaration order, return, and other capabilities. Avoid repeated derivative errors when a member is missing or its signature cannot be recovered. Preserve unassessed dependent obligations in evidence so completeness is accurate.

Render unknown and incompatible findings with different wording. A failure to prove compatibility is not proof that the candidate is wrong.

## Exception boundaries

`check()` does not raise ContractError for candidate outcomes. It can raise ContractDefinitionError for definition work and ordinary argument errors for invalid API use. Expected candidate inspection limitations become unknown evidence. Cancellation, process-control exceptions, and unexpected engine bugs propagate.

Do not catch every exception around the entire engine. Catch known inspection/annotation failures at the boundary that can accurately classify them.

## Presentation contract

[EXPERIENCE_DESIGN.md](EXPERIENCE_DESIGN.md) owns the shared result/exception presentation. Rendering consumes existing evidence without candidate access or a second compatibility decision. Core str output is plain, deterministic, and free of ANSI sequences and implicit logging. Repr is compact; neither form calls candidate repr/str to construct a label.

Use [the illustrative scenarios](examples/report_scenarios.json) to review the intended language. Equivalent implementation tests must establish the actual evidence before these examples count as release validation. Source type and location strings must be escaped so control characters cannot inject terminal output.

When a legal call shape explains a mismatch, include an established symbolic template in ctx.call_shape. It is optional diagnostic context, not a generated behavioral test or a fabricated runnable call.

## Stability

0.1 documents the initial export fields and codes and calls out changes during 0.x. At 1.0, codes, location structure, serialized fields, and semantic meaning follow compatibility policy. Exact prose is not machine-stable. Human snapshots supplement structured assertions; they are not the primary correctness oracle.
