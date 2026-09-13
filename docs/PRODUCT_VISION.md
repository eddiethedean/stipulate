# Product Vision

## Promise

Define an ordinary Python structural interface once, then check dynamically loaded implementations against its declared contract with precise explanations.

Stipulate is useful where a type checker cannot see the concrete implementation: plugin discovery, driver selection, dependency configuration, framework extension points, and test doubles.

Pydantic is a useful benchmark for simple entry points and helpful errors. Its value-validation semantics are different: Stipulate checks structural declarations and callable compatibility.

## First experience

```python
from typing import Protocol
from stipulate import Contract

class Storage(Protocol):
    def read(self, key: str) -> bytes | None: ...

storage_contract = Contract(Storage)
storage = storage_contract.validate(candidate)
```

The user learns one contract object and two initial methods: `validate()` to require compatibility, `check()` to understand it. Existing implementations require no migration. Existing Protocol definitions remain usable in annotations and editors.

`validate()` defaults to strict evidence requirements and returns the original candidate. `strict=False` deliberately tolerates missing implementation type information as defined in the contract engine. It does not suppress known mismatches or enable unsupported features.

## What a successful check establishes

Every declared operation in the supported contract has compatible inspectable member capabilities, call shapes, and type declarations. This conclusion assumes the implementation honors its annotations and exposed signatures. It is a point-in-time metadata assessment.

Even complete evidence does not establish that method bodies behave correctly, that future returned values match annotations, that arbitrary descriptors are safe, or that later mutation preserves conformance. A current attribute value also does not establish its declared writable type.

The user-facing promise should say “checks compatibility against available declarations.” Reserve “proof” for a stated metadata relation and its assumptions. Do not market Stipulate as behavioral enforcement or as safe execution of untrusted plugins.

## User experience requirements

- Start with a complete, executable example and one useful failure.
- Return the original object with the interface type preserved.
- Explain the failing operation, expected capability, observed declaration, and actionable repair.
- Show unknown evidence separately from incompatible evidence.
- Never make an incomplete check look successful through truthiness.
- Keep internal compiler types and policy bookkeeping out of routine examples.
- Avoid coercion, automatic candidate mutation, hidden method calls, and required implementation decorators.
- Make repeated use natural by retaining a `Contract` object.
- Keep documentation examples aligned with the released API, with future designs explicitly labeled.

## Technical distinction

The same normalized member and type relations should support candidate checking and eventual interface evolution. The engine records evidence so that absence of metadata remains distinguishable from a demonstrated mismatch.

For gradual types, ordinary assignability and universal evolution guarantees are different questions. Reuse normalized rules and explicit relation contexts; do not turn permissive acceptance into a theorem about all implementations.

## Long-term experience

“Define. Validate. Evolve.” remains the product vocabulary. After runtime validation is trustworthy, versioned schemas, fingerprints, and directional comparisons can serve framework authors and CI systems.

The `class Foo(Interface):` declaration with `Foo.validate()` remains an experimental ergonomic goal. It is promoted only after both supported checkers and the runtime agree, without a required checker plugin. The 0.1 product stands on `Contract(Protocol)` independently.

## Non-goals

Stipulate does not replace static checking, instrument general function calls, execute behavioral pre/postconditions, enforce business logic, provide dependency injection, extract entire package APIs, or wrap validated objects by default.

It does not become a full implementation of every typing construct before shipping. It supports a precise subset and diagnoses the rest explicitly.

## Experience execution

[EXPERIENCE_DESIGN.md](EXPERIENCE_DESIGN.md) turns the UX requirements into concrete journeys, report states, presentation rules, and observed usability targets. [The quickstart](QUICKSTART.md) is the first-use reference. Delivery milestones must demonstrate complete user tasks instead of reporting only internal modules finished.

## Success criteria

A small plugin author can diagnose a missing parameter or incompatible return annotation immediately. A framework author can inspect uncertainty programmatically. A typed application receives a precise interface type. A release engineer can eventually assess evolution without treating unknowns as compatibility guarantees.

The roadmap defines which of these capabilities ships at each stage.
