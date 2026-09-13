# Design Decisions

These decisions own durable policy. ROADMAP.md owns release scope and focused specifications define behavior. The open-problem register records whether implementation acceptance tests have passed. Selecting a policy does not resolve its implementation gate.

## D001 — Name and purpose

Stipulate checks structural interface contracts against available runtime declarations. The package is stipulate. “Contract” does not mean executed preconditions, postconditions, or business invariants.

## D002 — Method-based 0.1 API

The supported 0.1 declaration path is standard Protocol plus Contract(Protocol). Users call contract.validate() and contract.check(). This supersedes earlier plans making Interface shorthand the mandatory first release syntax.

The shorthand class Foo(Interface) with Foo.validate() remains an experimental goal gated on complete runtime and checker evidence.

## D003 — Structural implementations

Implementations need no Stipulate inheritance, decorators, registration, or dependency. Protocol composition includes an explicit Protocol base. Ordinary subclasses without that marker are not silently promoted to structural types.

## D004 — Python typing foundation

The typing specification governs supported annotation relations. Execution-kind and evidence policies are explicit Stipulate additions. Never silently present checker-specific behavior as language semantics.

## D005 — No required checker plugins

Public usage requires no mypy/Pyright plugin or consumer ignores. Supported checker versions and feature flags are documented. First-party code remains Pyright strict permanently.

## D006 — TypeForm constructor; supersedes free-function authority

Use Contract's TypeForm[T] constructor relationship to infer the validated T. A type[T] free function is not a checker-neutral fallback for Protocol values. No public helper-function API is needed for ordinary validation.

TypeForm design probes pass the recorded local checker configurations; installed-distribution and release-version gates remain open. Do not substitute an unrelated object-typed constructor that loses the declaration/T relationship.

## D007 — Experimental runtime helpers stay outside protocol members

Any future Interface class-side helpers delegate to Contract and never become required instance members. Do not claim typed shorthand until both checkers, exact member discovery, inheritance, and packaging pass.

## D008 — Original object and bounded guarantee

Successful validation returns the candidate itself. It assumes the implementation honors its annotations and exposed signatures. It neither checks future values nor prevents mutation. Even complete evidence is a conclusion about declarations.

## D009 — Directional relations

Use call-shape containment, contravariant inputs, covariant outputs, and separate read/write capabilities. Preserve unknown evidence. Unsupported forms never pass through annotation equality.

## D010 — Strict by default; supersedes permissive default

validate() requires conclusive compatible evidence by default. strict=False tolerates only annotation_missing and gradual_type candidate uncertainty after all required structural checks pass. Other unknowns and all known mismatches fail.

check() is policy-independent. Unknown is false in boolean context. accepted(strict=...) makes policy acceptance explicit without changing status.

## D011 — Immutable snapshots with weak global ownership

Contract owns immutable ContractIR. Global caches use weak declaration keys and weak IR values, because IR may retain its declaration. Strictness is not a compilation key. Custom namespaces bypass shared caching. refresh=True creates a new snapshot while prior contracts remain unchanged.

## D012 — Evidence and both exception paths from 0.1

Expose CompatibilityResult, Evidence, ContractError, and ContractDefinitionError. Structured findings distinguish incompatible and unknown evidence. check() avoids ContractError for candidate outcomes but does not swallow definition errors or internal defects.

## D013 — Unsupported is explicit

Unsupported requirements fail construction. Unsupported candidate metadata produces non-permissible unknown evidence. Support means a feature's semantics pass positive, negative, unknown/error, checker, and version tests; returning unsupported is not support.

## D014 — Declarations and runtime values are separate

Core 0.1 checks supported declared capabilities and storage presence. It does not execute property getters or recursively validate current values. Matching current data cannot prove writable declaration compatibility.

## D015 — Introspection execution policy

Do not call candidate methods/getters/dynamic hooks for core checking. Default trusted annotation evaluation can execute annotation expressions; raw mode does not request such evaluation and may leave requirements unresolved. Neither mode is a sandbox. This supersedes the absolute promise of no arbitrary code during annotation resolution.

## D016 — Existing Protocols are the primary adoption path

Contract replaces the earlier InterfaceAdapter and ContractAdapter concepts. Keep Protocol names available as types and give contract instances distinct variable names.

## D017 — Specification-oriented conformance

Record specification expectations, checker versions, runtime policy differences, and Stipulate results for each supported case. Tests must include exact inferred types and intended negative diagnostics.

## D018 — Universal evolution is stronger than gradual acceptance

Share IR and relation handlers but make relation context explicit. Unknown/Any materialization cannot certify all old implementations or consumers remain compatible. Report implementer and consumer directions separately; unknown never silently passes CI.

## D019 — Public tooling follows semantic gates

schema(), fingerprint(), compare(), and CompatibilityReport are not in 0.1. Internal normalized IR is required now; portable schema, identity, and evolution guarantees are stabilized later before public examples encourage persistence.

## D020 — Python and dependency posture

Target CPython >=3.11 with an explicit tested minor-version matrix. No implicit PyPy claim. typing_extensions provides TypeForm as needed. Pydantic and CLI dependencies remain optional, with Pydantic integration post-1.0. Native code requires profiling evidence.

## D021 — Evidence precedes promotion

This checkout's historical prototype claims do not satisfy release gates. Keep versioned design probes, then reproduce them with the actual installed implementation. Do not mark an OTP resolved on documentation edits alone.

## D022 — Experience is a release criterion

Teach one Contract and two primary operations: validate() for enforcement and check() for investigation. Plain str/repr output, actionable repair guidance, and accurate uncertainty language are part of 0.1. A pure presenter consumes evidence; it never reclassifies compatibility for display. User-observed task completion gates public beta. See EXPERIENCE_DESIGN.md and OTP-029.

## D023 — Deliver complete user tasks early

Implement the smallest working declaration-to-result path before expanding the type/member matrix. Every delivery slice includes its public typing, meaningful error/unknown behavior, and executable example. Module completion alone is not a product milestone. The roadmap's supported subset remains unchanged.
