# Competition Evaluation

## Purpose

Stipulate is no longer scoped as only a runtime Protocol validator. Its intended category is a **contract engine for Python structural interfaces**.

The engine compiles explicit structural contracts, validates dynamic implementations, preserves evidence about what can and cannot be proven, and uses the same directional compatibility semantics to reason about interface evolution.

This changes the competitive set. Runtime type checkers remain relevant, but API compatibility and contract-evolution tools are now equally important adjacent systems.

## Stipulate's intended position

Stipulate aims to own this combination:

> **Standard Python structural typing + deep runtime interface assignability + evidence-backed compatibility + semantic interface evolution.**

The core semantic question is:

```text
provided contract <= required contract
```

Public capabilities can then share one engine:

```python
validate(Storage, candidate)
inspect_contract(Storage, candidate)
compare_interfaces(StorageV1, StorageV2)
compile_contract(Storage).schema()
compile_contract(Storage).fingerprint()
```

## Strategic differentiation

Stipulate should not win by supporting the largest number of arbitrary annotations, extracting the largest Python API graph, or performing the most call-site analytics.

It should win by making **explicit Python structural contracts** a first-class semantic object and making one compatibility relation useful across runtime validation, explanation, schemas, CI, and evolution.

Particularly important differentiators are:

- implementations do not need Stipulate inheritance, registration, or decorators;
- interfaces remain useful to normal static type checkers;
- compatibility is directional and based on assignability, not textual equality;
- unknown runtime evidence is preserved rather than silently converted to success/failure;
- implementer and consumer compatibility can be analyzed separately during evolution;
- schemas, snapshots, and fingerprints derive from canonical contract IR;
- runtime validation and interface evolution use the same semantic engine.

---

## Python `typing.Protocol`

### Role

`typing.Protocol` is the language-level foundation rather than merely a competitor.

### Strengths

- standardized structural typing;
- understood by mypy, Pyright, Pylance, IDEs, and typing-aware libraries;
- supports inheritance and generic protocols;
- no third-party dependency.

### Gap

Static checking naturally ends at dynamic loading/configuration boundaries, and `@runtime_checkable` provides much shallower runtime guarantees than Stipulate intends.

Protocol also does not provide a canonical contract artifact, evidence model, schema/fingerprint lifecycle, or semantic interface-evolution tooling.

### Stipulate strategy

Compose with Protocol semantics rather than replacing them.

**Competitive importance: Critical foundation.**

---

## Pydantic

### Role

Pydantic is Stipulate's primary developer-experience benchmark rather than a direct contract-engine competitor.

### Lessons

- declarative models can become infrastructure;
- compiled representations matter;
- structured errors are more valuable than booleans;
- adapters ease adoption;
- schemas turn models into tooling artifacts;
- predictable semantics and excellent documentation create ecosystem trust.

### Difference

Pydantic primarily validates data/value structures. Stipulate validates and compares structural capability contracts.

### Stipulate strategy

Match the quality bar for errors, adapters, compilation, schemas, and ergonomics without imitating data-validation semantics where they do not apply.

**Competitive importance: Critical UX benchmark.**

---

## Griffe

### Role

Griffe is the most important established adjacent competitor for the interface-evolution/tooling side of Stipulate.

It builds rich representations of Python package APIs and supports serialization and breaking-change analysis between versions.

### Overlap

- Python API modeling;
- signatures and annotations;
- serialized representations;
- breaking-change detection;
- CI/release tooling;
- API evolution analysis.

### Fundamental difference

Griffe begins from a Python package's public source/API surface and asks what changed.

Stipulate begins from an **explicit structural requirement contract** and asks what may safely satisfy it.

Stipulate therefore has a natural runtime operation that package API extraction does not replace:

```python
inspect_contract(Storage, dynamically_loaded_plugin)
```

and its evolution semantics can be defined through the same relation used for implementation validation.

### Stipulate strategy

Do not compete with Griffe on whole-package source extraction, docstring modeling, or general API documentation graphs.

Specialize the IR around structural contract semantics and make assignability/evidence deeper.

**Competitive importance: High established adjacent competitor.**

---

## ImpactGuard

### Role

ImpactGuard is a close adjacent project on API-change CI and evolution tooling.

Its product direction includes API snapshots, semantic change classification, CI enforcement, risk analysis, SemVer recommendations, and call-site/runtime impact information.

### Overlap

- snapshots/baselines;
- breaking-change detection;
- CI gating;
- compatibility reports;
- release/SemVer advice.

### Fundamental difference

Impact-style tools analyze inferred code APIs and their usage/exposure.

Stipulate's semantic object is an explicit structural contract. It should not need call-site analytics to establish whether one contract is assignable to another.

Stipulate also combines evolution analysis with runtime implementation conformance.

### Stipulate strategy

Do not compete on whole-code impact/risk analytics. Make contract semantics, directionality, evidence, and Protocol interoperability stronger.

**Competitive importance: Medium-to-high emerging adjacent competitor.**

---

## Typeguard

### Role

Established runtime type checking.

### Overlap

- runtime annotations;
- Protocol awareness;
- annotation resolution;
- difficult Python runtime typing edge cases.

### Difference

Typeguard primarily checks values crossing runtime function/type boundaries. Stipulate compiles and reasons about a complete interface contract and its evolution.

### Stipulate strategy

Study annotation/runtime edge cases; do not become a function-instrumentation system.

**Competitive importance: High adjacent runtime-typing relevance.**

---

## Beartype

### Role

Mature broad runtime type checking.

### Overlap

- runtime type-hint semantics;
- annotation normalization;
- performance/caching problems;
- Protocol-aware typing behavior.

### Difference

Beartype is intentionally broad. Stipulate's value comes from specializing in complete structural contracts and using them beyond one runtime type check.

### Stipulate strategy

Do not compete on annotation count or decorator instrumentation. Study implementation techniques and potentially evaluate narrow optional delegation only if semantics remain Stipulate-owned.

**Competitive importance: High adjacent runtime-typing relevance.**

---

## `zope.interface`

### Role

Mature historical runtime-interface system.

### Overlap

- explicit interfaces;
- runtime verification;
- adaptation/component-system lessons;
- interface metadata.

### Difference

`zope.interface` is its own interface ecosystem. Stipulate deliberately stays grounded in modern Python structural typing and does not require implementations to opt into a nominal/component model.

### Stipulate strategy

Study mature verification and ecosystem lessons without recreating the separate interface language.

**Competitive importance: High historical relevance.**

---

## Design-by-contract libraries (`icontract`, related tools)

### Role

These libraries use the word "contract" for runtime behavioral conditions such as preconditions, postconditions, and invariants.

### Difference

Stipulate contracts are primarily **structural capability contracts**.

```text
Stipulate:
    Can this implementation safely satisfy this interface?

Design by Contract:
    Does this execution satisfy behavioral predicates?
```

Both concepts can coexist in one application.

### Stipulate strategy

Use precise terminology in documentation and avoid claiming behavioral correctness Stipulate does not execute/prove.

**Competitive importance: Terminology-adjacent, not direct.**

---

## Buf, oasdiff, and schema compatibility tools

### Role

These are conceptual analogues from Protobuf/OpenAPI ecosystems.

They demonstrate the value of treating contracts as versioned semantic artifacts and rejecting breaking changes in CI.

### Relevance

A future:

```text
stipulate snapshot
stipulate check
```

should follow the same philosophy: compare semantic contracts, not source text.

### Difference

Stipulate applies this lifecycle to native Python structural interfaces and can additionally validate live runtime implementations.

**Competitive importance: Strong conceptual validation, different ecosystem.**

---

## `cargo-semver-checks` and typed-language API compatibility tools

### Role

These demonstrate that mature typed ecosystems benefit from semantic API compatibility tooling tied to their type systems.

### Relevance

Stipulate can provide a Python structural-interface analogue, especially for plugin/framework APIs.

### Difference

Python's runtime dynamism and structural Protocol model require an evidence-aware contract system rather than simply reproducing Rust's public API rules.

**Competitive importance: Conceptual analogue.**

---

## mypy and Pyright

### Role

Interoperability targets and behavioral references, not runtime competitors.

### Stipulate strategy

- no checker plugin required for the core structural-typing experience;
- maintain checker conformance fixtures;
- follow the Python typing specification as semantic authority when checkers differ;
- document runtime-only APIs honestly.

**Competitive importance: Critical interoperability targets.**

---

## TypedProtocol and small interface-validation packages

### Role

Prior art demonstrating interest in deeper runtime Protocol checking.

### Assessment

They overlap with Stipulate's original validator-only concept but are not currently strategic baselines for the expanded contract-engine architecture.

### Stipulate strategy

Track for completeness. Do not distort architecture or roadmap around feature-for-feature competition unless adoption or scope materially changes.

**Competitive importance: Low strategic importance.**

---

## Competitive matrix

| Capability | Protocol | Griffe/API diff | Runtime type checkers | Schema compatibility tools | Stipulate target |
| --- | --- | --- | --- | --- | --- |
| Native Python structural typing | Excellent | Observes Python APIs | Uses annotations | No | Excellent |
| Validate live dynamic implementation | Shallow presence | No | Type/value oriented | No | Core |
| Complete interface contract IR | Static declaration | Rich package/API model | No interface lifecycle | External schema | Core |
| Assignability-driven member semantics | Static | API-change rules | General typing | Schema-specific | Core |
| Explicit unknown evidence | No | Not runtime proof model | Varies | Usually deterministic schema | Core |
| Directional implementer/consumer evolution | Static reasoning only | Breaking API analysis | No | Compatibility modes vary | Core target |
| Canonical contract schema | No | Serializable API model | No | Yes | Core target |
| Semantic fingerprint/snapshot | No | Baselines possible | No | Common | Planned |
| Same engine for runtime + evolution | No | No live object validation | No evolution lifecycle | No Python object validation | Core differentiator |

## Defensible position

Stipulate should protect this formulation:

> **Compile Python structural interfaces into canonical contracts, validate arbitrary runtime implementations against them with explicit evidence, and use the same directional compatibility engine to evolve those contracts safely.**

That is more defensible than "better runtime Protocol checking" and more specialized than whole-package API diffing.

## What Stipulate should not become

Stipulate should not become:

- a replacement static type checker;
- a whole-package source/documentation model competing with Griffe;
- a call-site/risk analytics platform competing with ImpactGuard-style tools;
- a general function instrumentation framework;
- an arbitrary runtime type checker competing on annotation count;
- a dependency injection or plugin framework;
- a behavioral pre/postcondition engine;
- a nominal interface ecosystem;
- a proxy framework by default.

## Competitive monitoring triggers

Reevaluate before major releases and when:

- Python materially expands runtime Protocol validation;
- the typing specification adds runtime-oriented interface semantics;
- Pydantic adds first-class structural contract validation/evolution;
- Griffe adds explicit structural-contract conformance against live implementations;
- Typeguard or Beartype adds a compiled interface lifecycle/evolution abstraction;
- API-diff tools add Protocol-aware directional assignability semantics;
- a dedicated Python structural contract engine gains meaningful adoption;
- checker changes obsolete Stipulate's Interface bridge or class-side typing workaround.

Competition should reveal user expectations and useful implementation lessons, but Stipulate's roadmap should remain driven by correctness of its contract relation.