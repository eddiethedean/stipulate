# Design probes

These probes support the plan with reproducible evidence. They do not implement Stipulate or satisfy installed-package/runtime release gates.

- `contract_api.pyi` sketches the TypeForm constructor and result/validation signatures. Its `.py` counterpart raises on import to prevent accidental use as a validator.
- `positive.py` checks inferred types, ordinary structural implementations, explicit Protocol composition, and the planned constructor options.
- `negative.py` contains five intentionally invalid examples. Errors are expected; there are no suppressions.
- `legacy_type_parameter.py` records the checker disagreement for the rejected type[T] fallback. Its cast does no runtime validation.
- `runtime_assumptions.py` demonstrates the weak-key/strong-value retention trap, weak-value lifecycle, and annotation-expression evaluation with a harmless counter. It does not claim to test a production raw resolver or thread-safe cache.

## Recorded environment

Verified on 2026-09-12 with local CPython 3.11, Pyright 1.1.411, mypy 1.19.1, and typing_extensions 4.15.0. These are tested configurations, not inferred minimum versions. This mypy requires `--enable-incomplete-feature=TypeForm`.

## Reproduce from the repository root

The positive checker commands must return exit code 0:

```sh
pyright --project design_probes/pyrightconfig.json
mypy --strict --enable-incomplete-feature=TypeForm --no-incremental --cache-dir /tmp/stipulate-design-mypy-cache design_probes/positive.py design_probes/runtime_assumptions.py
python3 design_probes/runtime_assumptions.py
```

Negative commands must return exit code 1 for exactly the expected errors below:

```sh
pyright --project design_probes/pyrightconfig.json design_probes/negative.py --outputjson
mypy --strict --enable-incomplete-feature=TypeForm --no-incremental --cache-dir /tmp/stipulate-design-mypy-negative-cache design_probes/negative.py design_probes/legacy_type_parameter.py
```

| Case marker | Pyright | mypy |
| --- | --- | --- |
| nominal-subclass | reportAssignmentType | assignment |
| incompatible-parameter | reportAssignmentType | assignment |
| mismatched-type-argument | reportArgumentType | arg-type |
| return-type | reportAssignmentType | assignment |
| invalid-policy | reportArgumentType | arg-type |
| legacy type[T] argument | Accepted in the positive project run | type-abstract |

Expected totals: zero errors and warnings in the positive Pyright project; zero errors in the positive mypy invocation; five errors in the negative Pyright invocation; six errors in the negative mypy invocation. Checker notes are not additional errors. A nonzero exit due to missing dependencies or unrelated diagnostics does not count as a passing negative probe.

The runtime probe must show that a live snapshot keeps its declaration alive, releasing it allows collection with weak cache values, strong values prevent collection, and get_type_hints evaluates the supplied annotation expression.

## Promotion boundary

The actual package must reproduce these outcomes with its implemented public types and installed wheel/sdist, then pass the supported Python matrix. Static stubs alone cannot verify validation behavior, result truthiness, the permission to return T, annotation policy, or production cache correctness. See [the implementation plan](../docs/IMPLEMENTATION_PLAN.md) and [typing strategy](../docs/STATIC_TYPING.md).
