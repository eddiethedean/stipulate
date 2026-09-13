# Developer Experience Design

This document owns presentation and user journeys. INTERFACE_MODEL.md owns API semantics, CONTRACT_ENGINE.md owns evidence and enforcement, and ROADMAP.md owns release scope. Illustrative reports are design fixtures, not outputs from an implemented validator.

## Product character

Precise, quiet, and helpful. The first successful interaction should take one declaration, one Contract construction, and one validation call. The first failure should tell the user what operation is incompatible and what to change.

The public interface is the Python API, editor inference, readable results/exceptions, documentation, and eventual CLI. There is no separate dashboard, account, or hosted control plane in the core plan.

## One primary path

```python
storage_contract = Contract(Storage)
storage = storage_contract.validate(candidate)
```

Keep Storage available as a normal Protocol type. Teach validate() first. Introduce check() when the user needs to investigate or make a policy decision:

```python
result = storage_contract.check(candidate)
print(result)
```

Advanced evidence, namespace configuration, refresh, and permissive policy appear in task-specific guides. Do not lead with the public type inventory, compiler internals, or three alternative ways to validate the same object.

Interface shorthand remains an independent ergonomic experiment. Its promotion must reduce user work while preserving exact typing and structural behavior; shorter source alone does not justify an unreliable API.

## Journeys and completion criteria

| Journey | Starting point | Successful outcome |
| --- | --- | --- |
| First use | An existing Protocol and candidate | One validation call returns the original object with the Protocol type inferred |
| Repair a mismatch | ContractError or an incompatible check | The user identifies the member, failed relation, and an appropriate repair without reading the engine source |
| Adopt partly typed code | Known call shape, missing return annotation | The user sees UNKNOWN and deliberately chooses annotation work or limited permissive acceptance |
| Investigate unsupported metadata | A callable without a supported signature | The user sees the exact limitation; strict=False is never suggested as a workaround |
| Integrate a framework | Many candidate objects | One retained Contract, independent results, stable structured findings, no hidden logging |
| Evolve an API, later | Two explicit contracts | The user selects implementer/consumer impact and cannot mistake UNKNOWN for a compatibility guarantee |

## Result language

The same evidence determines text, Python properties, exceptions, and later CLI output. A presenter must never recompute compatibility or infer success from an empty errors list.

| Engine state | Leading phrase | Visual role | Meaning |
| --- | --- | --- | --- |
| COMPATIBLE | Compatible with Storage | Positive | All required declaration obligations are established |
| INCOMPATIBLE | Incompatible with Storage | Error | At least one declaration requirement is disproven |
| UNKNOWN | Compatibility unknown for Storage | Caution | No disproven requirement, but some obligations remain unestablished |
| Definition failure | Cannot compile Storage | Definition error | No candidate result exists |

Completeness is independent. An incompatible result can still contain unknown evidence. An empty Protocol is compatible, with “No required members” explicitly shown so users do not mistake it for a substantive capability check.

Use a separate policy line when enforcement is being discussed: “Rejected by strict validation,” “Accepted with missing type information,” or “Rejected: unsupported signature.” Permissive acceptance never recolors an UNKNOWN result as compatible. Merely inspecting a result does not emit a policy line for a policy the caller did not select.

## Diagnostic anatomy

Each actionable issue has:

1. A member path, such as read.key.
2. A plain-language failed obligation or missing fact.
3. Required and provided declarations, labeled in that order.
4. One appropriate next step.
5. A stable code and evidence category for tools.

For call-shape mismatches, show a symbolic required call when the deterministic algorithm can establish one without execution. Example: `read(key=<str>, fresh=<bool>)`. Label it “Required call shape”; placeholders are not runnable arguments. Do not execute a candidate or synthesize arbitrary user-type instances to generate an example.

For parameter types, explain the values the contract permits. For return types, explain what callers are allowed to expect. Avoid “types differ” when the actual problem is directional assignability.

Repair guidance must not tell users to falsify annotations. “If the method already accepts text, correct its annotation; otherwise update its implementation” is appropriate when behavior is unknown. Do not automatically rewrite source from introspection findings.

## Plain-text presentation in 0.1

`str(result)` is a readable report, `repr(result)` is a compact state summary, and str(ContractError) adds the selected policy and rejected findings. Both use a shared presenter over immutable evidence. Successful validate() is silent and returns the original object.

Canonical compact representations:

```text
Contract[Storage]
CompatibilityResult(status='unknown', complete=False, errors=0, unknowns=1)
```

Counts describe public finding records, not fabricated percentages, confidence, members passed, or benchmark timing. Display names are safe metadata labels and do not imply portable type identity.

A plain report shows all actionable incompatible and primary unknown findings. Dependent unassessed facts stay in evidence and appear as one aggregate line when needed; they do not flood the user with derivatives of the same root problem. Rendering must not hide unrelated failures. Optional future UIs may collapse details but must show exact counts and offer expansion.

Long output may be bounded only with an explicit omitted-count message and an available full-output path. Do not silently truncate the underlying findings. Initial Python str output remains complete for actionable findings; line wrapping and abbreviation of long type labels must preserve access to the full exported metadata.

## Rendering behavior

- Core Python string output is plain text with no ANSI sequences, hidden stdout/stderr writes, or Rich dependency.
- Prefer a readable single-column layout at 80 columns and preserve legibility at 60; wrap explanatory text and indent continuations. Keep identifiers identifiable even when long.
- Meaning survives copying to a log, pasting into an issue, or reading without color.
- Never call candidate repr/str or property getters to decorate a report. Use already collected, sanitized metadata. Escape control characters and terminal escape sequences in names and annotation text.
- Do not render candidate values, secrets, or full namespace mappings. Reporting does not add access beyond compilation/inspection policy.
- Unknown wording is neutral; incompatible wording is specific. Avoid blame, unexplained jargon, and a large warning banner for routine missing annotations.
- A browser-based preview uses semantic controls, text status labels, visible keyboard focus, accessible details, and live status updates without moving focus.

## Example catalogue

[The report scenarios](examples/report_scenarios.json) define illustrative cases for compatible, incompatible parameter, call shape, missing type information, unavailable signature, mixed evidence, invalid definition, and empty contract states.

Each fixture records engine status, completeness, allowlisted acceptance, primary findings, and display text. The interactive design preview uses these facts; it is not connected to a live validation engine. During implementation, equivalent runtime tests must produce matching semantic records before the fixtures can count as product evidence.

Keep display text expectations separate from semantic record assertions. Improve wording without obscuring stable codes or changing acceptance to make a screenshot look better.

## Documentation architecture

The README leads with a complete example and one failure. The learning path is:

1. [Quickstart](QUICKSTART.md): define, validate, inspect, repair.
2. [Public API](INTERFACE_MODEL.md): exact behavior and return types.
3. [Understanding results](CONTRACT_ENGINE.md): uncertainty and enforcement.
4. [Typing setup](STATIC_TYPING.md): supported checker settings.
5. [Supported features](ROADMAP.md): release-specific boundaries.
6. Focused troubleshooting for annotations, properties, signatures, and mutation.

Every page distinguishes released, planned, and experimental capabilities. Until Stipulate has a verified distribution, do not publish an installation command that could install an unrelated package with the same name.

## Later CLI design

CLI implementation follows schema and comparison gates. Design its behavior now without adding it to 0.1: plain output when redirected, optional terminal styling with text labels, explicit JSON output, stable exit-code categories for compatible/incompatible/unknown/definition failures, and help/examples that name the comparison direction.

Do not silently import arbitrary snapshot type names, default UNKNOWN to exit-code success, or emit colored prose into JSON output. Freeze exact commands and exit codes with the CLI's own acceptance tests rather than inventing a second checker API here.

## Experience verification

Phase 0.1 requires executable installed-package examples, accurate outcome language, supported-boundary documentation and safe readable reports. The user withdrew the five-person participant-study requirement. Participant research is optional follow-up work and does not block release.

When usability feedback identifies a problem, revise the documentation, API or diagnostic and verify the affected behavior without relaxing correctness.
