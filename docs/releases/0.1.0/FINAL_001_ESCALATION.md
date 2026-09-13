# FINAL-001 escalation decision and remediation

The user authorized this task to resolve the escalation. The decision below
supersedes the earlier unresolved escalation and the owner-recovery assumption
introduced in `8608f94`. It does not grant independent release approval.

## Decision

A function's current qualified global name and its exposure by any class do not
establish its lexical declaring owner. Replacement classes can reuse a function
through an ordinary method, a decorator factory, a property, or direct assignment.
The original class can also be collected while the function remains alive.
Searching aliases or examining wrapper implementation patterns cannot recover
information that is no longer present.

For a selected function reached through `__wrapped__`:

- Use the code object's lexical qualified name to distinguish a free function
  from a class-defined function. `functools.wraps` copies function `__qualname__`,
  so that attribute cannot establish the selected code's lexical origin.
- A free function uses its own module globals under the existing namespace policy.
- A class-defined function may use its compiler-created `__class__` closure to
  obtain the declaring class. This cell is present when the method refers to
  `__class__`, including through zero-argument `super`; reading it executes no
  candidate operations and does not depend on current global bindings.
- If that class context is unavailable, use the existing unresolved-owner path.
  Name-dependent annotations produce non-permissible `annotation_unresolved`;
  neither strict nor permissive validation accepts that uncertainty. Even a
  global or builtin name cannot replace unknown owner-local precedence.
- Materialized annotations and independent obligations remain usable. Explicit
  requirement `localns` can resolve names; candidate resolution continues to
  exclude constructor namespace overrides.

This is a conservative availability boundary within the existing annotation and
signature abstractions. It needs no new public API, registration mechanism,
dependency, global object scan, or ownership cache. Declarations inspected directly
in their declaring class retain the existing static owner context.

The [approved contract](../../PHASE_0_1_IMPLEMENTATION_CONTRACT.md),
[implemented behavior](../../IMPLEMENTED_0_1.md), and
[type-system policy](../../TYPE_SYSTEM.md) now explicitly record this decision.

## Verification adjudication

Earlier implementation-side controls expected complete resolution for ordinary
wrapped/decorated methods solely because a global class exposed the selected
function. That expectation is superseded: without recorded owner context, those
cases must report unresolved evidence. The inputs remain represented by tests,
with explicit assertions that both enforcement modes reject them.

Additional positive controls exercise recorded owner cells for ordinary methods
and property accessors, including falsey metaclasses and replacement globals.
They continue to produce the correct complete type mismatch without executing
candidate code. Materialized types remain compatible in both trusted and raw
modes; free-function globals remain usable despite copied class metadata.

All Sol-authored verification artifacts are unchanged. The protected
[review-04 test](../../../tests/test_sol_review_04_blockers.py) retains SHA-256
`67082053f0f92e6a3c4038d37e40e876d0245be7d5b6d5addcbed2a26f1cc1c8`.

## FINAL-001 — Wrapped-function exposure does not establish its defining owner

Status: **FIXED**.

Related AC: AC-005, AC-008, AC-014, with the explicit escalation decision above.

Root cause: `_defining_owner()` followed a qualified global name and accepted a
class if `_exposes_function()` found the selected function in a member/wrapper
chain. The class could be a replacement with different annotation locals, causing
false complete compatibility.

Production changes: `src/stipulate/_signatures.py::_defining_owner` now uses the
selected code's lexical origin and recorded class cell. Removed `_exposes_function`
and the global/member ownership inference. The existing annotation resolver
handles unavailable owner context without new exceptions or acceptance rules.

Before-fix verification: the protected review-04 test failed with complete,
compatible acceptance. The original suite had 187 passes and that one failure.
An independent factory-wrapper probe reproduced the same false acceptance after
the original class was collected, ruling out retained-alias lookup as a solution.

After-fix verification: the unchanged protected test passes on Python 3.11–3.14
as part of the full source-quality matrix, 198 tests on each runtime.

Related regression tests: the full corpus includes previous Sol blockers,
annotation-layer precedence, raw annotation handling, explicit requirement
namespaces, independent mismatches, method/property behavior and lifecycle checks.

Additional tests: direct reuse and factory wrappers after global replacement;
collected versus class-cell-retained original owners; decorated method/property
availability with and without class cells; falsey metaclass owner recovery;
materialized types under both policies; and selected free-function globals despite
copied class-qualified metadata. These exercise the provenance boundary without
special-casing Sol's input.

Resolution: wrapped targets either use recorded declaring-owner context or retain
non-permissible uncertainty. A replacement class's namespace no longer supplies
inferred annotation locals. No finding was downgraded and no protected verification
or quality gate was weakened.

## Quality gates recorded during remediation

| Gate | Executed | Result |
| --- | --- | --- |
| Source runtime suite, Python 3.11–3.14 | Yes | PASS, 198 tests each |
| All protected Sol verification | Yes | PASS, included in each runtime |
| Ruff lint and formatting | Yes | PASS, all four environments |
| Strict Pyright and mypy | Yes | PASS, all four environments |
| Positive/negative design probes and runtime probes | Yes | PASS, all four environments |
| Documentation checks | Yes | PASS, all four environments |
| Canonical wheel build and installed-wheel benchmark | Yes | PASS, ten workloads |

Clean installed-distribution checks and the final commit's CI results are reported
in the task handoff. This report does not claim an unexecuted check passed.

## Scope and handoff

Existing Sol FOLLOW-UPs: none. New follow-up candidates: none.
All production changes address FINAL-001. The benchmark was regenerated because
its source digest and wheel hash must identify the corrected implementation.

Blockers received: 1. Blockers fixed: 1. Blockers remaining: 0.
Verification conflicts: 0. Escalations remaining: 0. New follow-up candidates: 0.

**READY FOR SOL RE-REVIEW**
