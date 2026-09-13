# Performance and Caching

## Goal

Make validation inexpensive enough for plugin loading, dependency setup, and test setup. Optimize repeated requirement compilation without weakening per-candidate checks. No numeric performance claims are made before measurements.

## Ownership and weak cache

A Contract facade strongly owns its immutable ContractIR. The IR may strongly own the declaration and source type objects. The process-wide compilation cache uses weak keys AND weak references to IR values:

```text
WeakKeyDictionary[declaration, dict[CompilationKey, weakref(ContractIR)]]
Contract -> ContractIR -> declaration
```

This is conceptual pseudocode. The IR implementation must support weak references. CompilationKey contains stable scalar policy values and must not retain the declaration indirectly.

A weak-key dictionary with strong IR values is rejected: cache -> IR -> declaration keeps its own key alive. A self-referential annotation can create the same problem even if a direct declaration field is removed. Do not rely on weak keys alone.

With no live Contract owner, the IR can expire and the next request can recompile. Reusing a Contract is the intended high-throughput path. Do not promise a permanently warm global cache for unretained temporary adapters.

## Cache keys

Compilation keys include annotation policy and any feature/configuration choice changing interpretation. Strictness is excluded because it only affects enforcement. Custom globalns/localns bypass shared caching in 0.1; copying a namespace mapping does not freeze referenced objects or make namespace identity a safe cache key.

Two live Contract facades may share the same immutable IR. Facade object identity is not a public cache guarantee; each facade's .contract property is itself.

## Mutation and refresh

A Contract is a requirement snapshot. Candidate checking always inspects current candidate metadata. No successful-candidate cache is enabled by default.

Interface mutation is not tracked automatically. `Contract(Storage, refresh=True)` compiles a new snapshot and updates the shared cache entry on success. Existing Contract objects keep their previous snapshots. Failed refresh does not replace a valid cache entry. Document that imported annotation dependencies can change too.

Refresh is not a compilation-key dimension. It forces new compilation even when an otherwise matching entry is live. No public global clear-cache function is required for 0.1; tests may use an internal reset.

## Concurrency

Protect weak-cache lookup and publication with a small lock. Never hold it during annotation evaluation, candidate inspection, or relation checking. Duplicate concurrent compilation is permitted. On ordinary first-use races, publish or reuse a live equivalent entry; refresh publication must atomically replace the selected entry.

No exactly-once annotation-evaluation guarantee is made. Compilers retain strong local references while working. Candidate state is per-call. Do not cache exception instances or tracebacks: they retain frames, namespaces, and potentially candidates.

## Required lifecycle tests

- Repeated validation through one Contract reuses its IR.
- Two retained contracts can share cached metadata.
- A temporary local Protocol and recursive source references are collected after all external owners are released.
- Cache keys, values, callbacks, locks, failures, and namespace options do not retain dead declarations.
- A live Contract intentionally keeps its own snapshot usable.
- Refresh leaves prior snapshots unchanged and does not cache failed work.
- Concurrent compilation, refresh, and validation do not share mutable evidence or deadlock.
- Candidate monkey-patching is observed on the next check.

## Candidate cost

Requirement compilation does not eliminate candidate signature and annotation inspection. Measure these separately. Cache candidate metadata only after a future explicit invalidation design; never claim all get_type_hints or signature costs disappear after requirement compilation.

## Benchmarks

Record cold compilation, warm retained-Contract validation, temporary Contract construction, positive/negative/unknown results, strict/permissive enforcement, large contracts, inheritance, and deep supported types. Keep performance benchmarks separate from correctness CI thresholds.

Do not compare against shallow isinstance checks as if the guarantees were equivalent. Add a native core only when profiles identify an actionable engine bottleneck.
