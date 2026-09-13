# Compatibility Policy

## Runtime targets

Planned minimum: CPython 3.11, with requires-python >=3.11 in future package metadata. The initial release test targets are CPython 3.11, 3.12, 3.13, and 3.14. This design checkout does not yet claim tested Stipulate support on any of them.

Advertise a minor version only after compilation, annotation resolution, signature normalization, supported type relations, evidence, lifecycle, and installed-package tests pass. Import success is insufficient. PyPy and other implementations are outside the initial support claim.

Newer annotation metadata must be handled deliberately, including deferred evaluation. New interpreter features do not automatically expand the supported type-form subset. Use typing_extensions when its behavior is tested; do not invent unavailable runtime metadata.

## Checkers and packaging

Pyright strict is permanent for first-party code. Public fixtures also run on supported mypy configurations. Record exact versions and required feature flags; the current design probe's mypy 1.19.1 requires its TypeForm flag. No required checker plugin or consumer ignores.

The TypeForm constructor and inferred return type are part of the public contract. Test installed wheels and sdists outside the source tree with py.typed and any required stubs present. Do not claim that local declaration probes prove package behavior.

## Typing semantics and runtime policy

The typing specification governs supported annotation relations. Strict evidence, trusted/raw annotation evaluation, static inspection limits, and the initial coroutine-kind rule are explicit Stipulate policies. Document intentional differences from ordinary checker assignment behavior.

Supported constructs form a versioned subset. New support can turn UNKNOWN into COMPATIBLE or INCOMPATIBLE; treat resulting acceptance changes as observable behavior and explain them in release notes. Never market strict validation as method-body or future-value enforcement.

## Versioning

During 0.x, call out breaking API, policy, diagnostic, or supported-subset changes clearly. At 1.0, semantic versioning covers documented Python APIs, supported compatibility semantics, enforcement defaults, diagnostic fields/codes, and public schema versions.

Correctness fixes can legitimately reject previously accepted candidates. Classify and document their impact; do not quietly claim acceptance is unchanged because a change is a bug fix.

## Schema and diagnostics

Public schema()/fingerprint() follow their later release gate, including explicit schema versions and identity/portability policy. Internal IR records are not a public interchange format.

Diagnostic location, code, serialized fields, and semantic category become stable at 1.0. Exact human wording remains free to improve. Unknown and incompatible categories must remain distinguishable.

## Mutation and evaluation

Contracts are immutable requirement snapshots; refresh=True makes a new snapshot. Candidate checks are point-in-time and are repeated after candidate mutation. Trusted annotation evaluation can execute expressions; raw mode does not request evaluation and can produce unresolved evidence. Neither mode is a security boundary.

## Dependencies and integrations

Core results must not change merely because Pydantic or another optional integration is installed. Third-party annotation metadata is not supported implicitly. Raising Python/dependency minimums requires an explicit compatibility decision and a tested migration path.

## Deprecation

At 1.0, announce deprecations and normally retain them through at least one minor release, with removal in a major release. An exceptional correctness/security removal must explain why ordinary deprecation was insufficient.
