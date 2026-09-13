# Dependency Strategy

## Core

Start with standard-library dataclasses, inspect, typing, weakref, and explicit typed internal records. Stipulate owns its IR, type relations, evidence, and enforcement semantics.

Use typing_extensions for TypeForm and supported cross-version features. The recorded design probes use 4.15.0; treat that as the initial tested baseline, not proof of the oldest compatible release. Freeze actual package minimums only after the release matrix passes.

attrs and typing-inspection remain optional implementation evaluations, not commitments. Adopt them only if conformance experiments demonstrate a meaningful correctness or maintenance benefit. Do not add a dependency because it resembles a small standard-library abstraction.

## Development

Use pytest, Hypothesis, Ruff, Pyright strict, and mypy public fixtures. Pin tested checker versions and document required TypeForm settings. The specification is the semantic reference; checker/runtime-library disagreement needs an explanation rather than majority voting.

Keep design probes separate from implementation tests. A local fixture dependency is not automatically a production dependency.

## Later CLI

Typer and Rich are preferred candidates for an optional stipulate[cli] extra once snapshot and comparison APIs are ready. CLI code consumes the shared contract engine and emits machine-readable reports independently of terminal rendering.

No CLI dependency is needed for library validation or the 0.1 API.

## Optional integrations

Pydantic is optional and post-1.0. It must not become the assignability engine or change core outcomes based on installation state. Integration value validation needs its own no-hidden-coercion and attribute-access policy.

Griffe may be evaluated if later work needs package API extraction. Typeguard and other runtime typing libraries can inform narrow differential experiments but do not define Stipulate's structural assignability semantics.

## Optimization

Use hashlib and json for future schema tooling once canonical semantics exist. Do not introduce Rust, PyO3, or native build infrastructure before profiling identifies a material bottleneck. Keep Python introspection on the Python side of any future native boundary.

## Acceptance rule

A dependency must demonstrably remove difficult non-differentiating work, improve tested compatibility, or provide a justified optional capability. Record its purpose, supported versions, typing quality, and effect on the package matrix before adoption.
