# Compatibility Policy

## Scope

Stipulate sits at the intersection of Python runtime introspection and Python's evolving typing system. Compatibility therefore includes more than ordinary API stability.

The project must track Python runtime versions, `typing` semantics, `typing_extensions` where needed, mypy behavior, Pyright/Pylance behavior, public Stipulate API stability, structured error stability, and contract schema stability.

## Python versions

**Minimum supported Python version: 3.11.**

Package metadata should declare:

```toml
requires-python = ">=3.11"
```

The project should test every supported minor version in CI.

The initial matrix should include Python 3.11 and every newer generally available Python release that Stipulate supports. New Python versions should be added promptly once dependencies and CI tooling are ready.

Do not claim compatibility with a Python version unless the `Interface` bridge, annotation resolution, signature normalization, contract compilation, runtime validation, and typing fixtures pass on that version.

### Newer-version typing features

The package-wide minimum should not be raised merely to use newer typing features.

Stipulate may provide richer behavior conditionally on newer Python versions when the runtime exposes additional typing metadata or semantics. For example, Python 3.12+ features may receive enhanced support while Python 3.11 remains fully supported for the documented 3.11 feature set.

Use `typing_extensions` where it provides a correct and mature compatibility bridge. Do not emulate runtime metadata that does not actually exist on older interpreters.

### Raising the minimum

Raising the minimum Python version is a deliberate compatibility decision. It should happen only when maintaining the older version materially harms correctness, maintainability, security, or access to required typing/runtime capabilities.

## Private typing internals

The prototype demonstrates that runtime protocol machinery can be composed successfully, but private implementation details such as `_ProtocolMeta` must not become public API.

Where private behavior is unavoidable internally, isolate it behind a compatibility module and test it across all supported Python versions.

## Static checkers

Pyright strict is the first-party typing standard for Stipulate itself. The repository must remain clean under Pyright `typeCheckingMode = "strict"` from the first implementation onward.

The public user experience must remain useful without checker-specific plugins. Compatibility fixtures should cover both Pyright and mypy.

## Typing specification

Python's typing specification is the primary semantic reference for assignability rules. Checker behavior is useful evidence, but Stipulate should not blindly copy checker-specific bugs or extensions.

## Semantic versioning

Before 1.0, rapid iteration is expected, but breaking changes should still be called out clearly.

For 1.0 and later, semantic versioning should cover public Python APIs, compatibility semantics for supported constructs, documented configuration behavior, stable structured error fields/codes, and serialized contract schema versions.

## Schema versioning

`schema()` output should contain an explicit schema version before consumers are encouraged to persist or exchange it.

Changes that alter serialized meaning should bump the schema version even when the Python package remains within a compatible API release.

## Error compatibility

At 1.0, error type codes, location structure, and broad semantic meaning become stable. Exact prose should not be considered machine-stable.

## Runtime mutation

Validation is a point-in-time assertion. A validated implementation can potentially be monkey-patched later. Stipulate does not guarantee future conformance unless a future explicit enforcement/proxy feature is used.

## Third-party typing constructs

Support for third-party annotation systems should not be implied automatically. Integrations may be added deliberately, but the built-in Python typing model remains the baseline.

## Deprecation policy

Once 1.0 is reached, public API deprecations should normally remain for at least one minor release before removal unless retaining them creates a correctness or security issue.
