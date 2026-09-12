# Compatibility Policy

## Scope

Stipulate sits at the intersection of Python runtime introspection and Python's evolving typing system. Compatibility therefore includes more than ordinary API stability.

The project must track:

- Python runtime versions;
- `typing` semantics;
- `typing_extensions` where needed;
- mypy behavior;
- Pyright/Pylance behavior;
- public Stipulate API stability;
- structured error stability;
- interface schema stability.

## Python versions

The initial release should target a modern minimum Python version and test every supported minor version in CI.

Do not claim compatibility with a Python version unless the `Interface` bridge, annotation resolution, signature normalization, and typing fixtures all pass on that version.

## Private typing internals

The prototype demonstrates that runtime protocol machinery can be composed successfully, but private implementation details such as `_ProtocolMeta` must not become public API.

Where private behavior is unavoidable internally, isolate it behind a compatibility module and test it across all supported Python versions.

## Static checkers

The core user experience must remain useful without checker-specific plugins.

Supported checker behavior should be tested against:

- mypy;
- Pyright.

Stipulate may document differences when the checkers disagree, but should avoid APIs that only one checker can understand when a portable alternative exists.

## Typing specification

Python's typing specification is the primary semantic reference for assignability rules.

Checker behavior is useful evidence, but Stipulate should not blindly copy a checker bug or checker-specific extension unless explicitly documented.

## Semantic versioning

Before 1.0, rapid iteration is expected, but breaking changes should still be called out clearly.

For 1.0 and later, semantic versioning should cover:

- public Python APIs;
- validation semantics for supported constructs;
- documented configuration behavior;
- stable structured error fields and codes;
- serialized interface schema versions.

## Schema versioning

`interface_schema()` output should contain an explicit schema version before consumers are encouraged to persist or exchange it.

Changes that alter serialized meaning should bump the schema version even when the Python package remains within a compatible API release.

## Error compatibility

At 1.0, treat these as stable:

- error `type` codes;
- `loc` structure;
- broad meaning of `msg`.

Exact prose should not be treated as machine-stable.

## Runtime mutation

Validation is a point-in-time assertion. A validated implementation can potentially be monkey-patched later.

Stipulate does not guarantee future conformance unless an explicit future proxy/enforcement feature is used.

## Third-party typing constructs

Support for third-party annotation systems should not be implied automatically. Integrations may be added deliberately, but the built-in Python typing model remains the baseline.

## Deprecation policy

Once 1.0 is reached, public API deprecations should normally remain for at least one minor release before removal unless retaining them creates a correctness or security issue.
