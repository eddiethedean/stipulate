# Performance and Caching

## Principle

Deep interface validation is necessarily more expensive than Python's shallow runtime protocol checks. Stipulate should therefore optimize around **compile once, validate many** rather than repeatedly resolving the same interface metadata.

## Compiled contracts

The central optimization is `CompiledInterface`.

```text
Interface class
    -> expensive compilation once
    -> cached CompiledInterface
    -> inexpensive repeated candidate validation
```

Compilation may include:

- inherited member discovery;
- type-hint resolution;
- forward-reference resolution;
- signature normalization;
- member classification;
- normalization of typing constructs;
- precomputed validation strategies.

## Cache design

The default cache should avoid keeping user-defined interface classes alive indefinitely.

Prefer weak-reference-based caches where possible.

Conceptual design:

```python
WeakKeyDictionary[type, dict[ConfigKey, CompiledInterface]]
```

Configuration that changes compilation semantics must participate in the cache key.

## Thread safety

Compilation caches must be safe for concurrent reads and first-use compilation.

Avoid holding global locks during candidate validation. A small lock around cache population is acceptable if profiling supports it.

## Adapter reuse

Frameworks and hot paths should use `InterfaceAdapter`:

```python
validator = InterfaceAdapter(Storage)

for plugin in plugins:
    validator.validate_python(plugin)
```

The adapter owns or references one compiled interface and avoids repeated public API dispatch.

## Candidate caching

Do not cache successful candidate validation globally by default.

Python objects and classes can be monkey-patched, descriptors can change, and dynamic implementations may alter members after validation. Caching candidate success could therefore create correctness surprises.

A future opt-in class-level conformance cache may be considered for immutable/stable implementations, but it must have explicit invalidation semantics.

## Introspection cost

Prefer static inspection functions where possible. Avoid repeated `inspect.signature()` and `get_type_hints()` calls after compilation.

Implementation signatures may also be normalized during validation and could be cached by callable/class identity when safe, but this is secondary to interface compilation caching.

## Error collection cost

Default validation should aggregate useful errors, even though fail-fast behavior can be faster.

A future `fail_fast=True` option may be considered for hot paths, but correctness and diagnostic quality are more important for the initial API.

## Benchmarks

Performance benchmarks should include:

1. cold interface compilation;
2. warm validation using the global cache;
3. warm validation through `InterfaceAdapter`;
4. successful validation;
5. multi-error invalid implementations;
6. interfaces with many methods;
7. deep interface inheritance;
8. forward references and complex annotations.

Benchmarks should compare trends between releases rather than advertise unrealistic parity with `isinstance()`.

## Performance target

The primary target is not to beat shallow protocol checks. It is to make deep validation cheap enough to use naturally at application boundaries, plugin loading, dependency setup, test setup, and framework registration.

Stipulate is not intended to revalidate an object on every method call unless a future proxy/enforcement feature explicitly provides that behavior.
