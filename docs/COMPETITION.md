# Competition Evaluation

## Purpose

Stipulate occupies the intersection of Python structural typing, runtime type validation, and interface contracts. This document evaluates the projects and standards most relevant to that position.

The goal is not to copy competitors feature-for-feature. Stipulate should use the Python typing specification as its correctness baseline, established type checkers as interoperability targets, and mature validation libraries as quality benchmarks.

## Stipulate's intended position

Stipulate answers a specific question:

> Does this object safely implement this structural interface?

The intended experience is:

```python
from stipulate import Interface, validate


class Repository(Interface):
    def get(self, id: int) -> User | None: ...
    async def save(self, user: User) -> None: ...


repo = validate(Repository, candidate)
```

The same interface should remain useful to ordinary Python static type checking.

Stipulate is therefore not primarily a general-purpose runtime type checker and should not attempt to compete by supporting arbitrary annotations in every possible runtime context before its interface-validation semantics are correct.

## Evaluation criteria

Relevant alternatives are evaluated against these capabilities:

1. standard Python structural typing interoperability;
2. deep runtime validation of complete interfaces;
3. callable assignability rather than signature equality;
4. attributes, properties, methods, and async methods;
5. generic and advanced typing semantics;
6. structured diagnostics;
7. compiled/cached validation;
8. schema or machine-readable contract metadata;
9. adoption cost for existing Python code;
10. maturity and ecosystem significance.

---

## Python `typing.Protocol`

### Role

`typing.Protocol` is not merely competition. It is the language-level foundation Stipulate is designed to extend at runtime.

### Strengths

- standardized structural typing;
- understood by mypy, Pyright, Pylance, IDEs, and typing-aware libraries;
- supports protocol inheritance and generic protocols;
- no third-party dependency;
- defines the user expectation for structural substitutability.

### Runtime gap

`@runtime_checkable` primarily provides member-presence checks. It does not deeply establish that callable signatures, annotations, async behavior, properties, and related interface semantics are compatible.

### Stipulate strategy

Do not replace Protocol semantics. Compose with them.

Stipulate interfaces should remain useful as ordinary structural types while adding a deeper runtime contract layer.

### Competitive importance

**Critical.**

The primary adoption question is not whether Stipulate is better than Protocol. It is whether Stipulate adds enough runtime value while preserving Protocol's static value.

---

## Pydantic

### Role

Pydantic is not a direct interface-validation competitor. It is Stipulate's most important developer-experience benchmark.

Pydantic demonstrates what Python developers increasingly expect from a serious validation system:

- declarative models;
- a clear validation entry point;
- compiled validation machinery;
- predictable behavior;
- structured errors;
- adapters;
- schema generation;
- excellent introspection and tooling ergonomics.

### Difference

Pydantic primarily validates data/value structures. Stipulate validates behavioral/object contracts.

Conceptually:

```python
User.model_validate(data)
```

corresponds to:

```python
validate(Repository, candidate)
```

### Stipulate strategy

Treat Pydantic as the UX quality bar, not as an implementation dependency or type-system authority.

Stipulate should aspire to similarly useful errors, adapters, compiled metadata, stable APIs, and documentation while retaining semantics appropriate for interfaces.

### Competitive importance

**Critical UX benchmark.**

---

## Typeguard

### Role

Typeguard is an established runtime type-checking library and a serious adjacent competitor.

Its core purpose is runtime enforcement of type annotations on values, arguments, return values, generators, and related execution boundaries.

### Strengths

- mature runtime type-checking ecosystem;
- broad annotation support;
- instrumentation and decorator workflows;
- existing awareness of Protocol types;
- useful prior art for annotation resolution and difficult runtime typing cases.

### Difference from Stipulate

Typeguard's primary abstraction is runtime checking of values against type annotations.

Stipulate's primary abstraction is compilation and validation of an entire structural object contract.

Stipulate must reason about relationships among interface members and candidate members, including callable parameter direction, return direction, call shape, member kinds, inheritance, and eventually generic bindings.

### Stipulate strategy

Study Typeguard's behavior for annotation handling, forward references, decorators, unsupported constructs, and runtime edge cases.

Do not turn Stipulate into a competing function-instrumentation system.

### Competitive importance

**High adjacent relevance.**

---

## Beartype

### Role

Beartype is a mature, broad runtime type-checking system with extensive support for Python type hints.

### Strengths

- broad runtime typing support;
- mature optimization work;
- sophisticated annotation handling;
- decorators and lower-level checking APIs;
- substantial implementation experience around difficult Python typing constructs.

### Difference from Stipulate

Beartype is fundamentally broader. Its mission is runtime type checking across Python annotations.

Stipulate should specialize in interface contracts and make that specialization materially better than treating an interface as just another runtime type hint.

### Stipulate strategy

Do not compete on total number of supported arbitrary type hints or decorator instrumentation.

Study Beartype for performance techniques, annotation normalization, caching, and runtime typing edge cases.

Potential future integration or optional delegation of narrow low-level type operations may be investigated only if it does not compromise Stipulate's semantics or dependency profile.

### Competitive importance

**High adjacent relevance; not the product model to copy.**

---

## zope.interface

### Role

`zope.interface` is important mature prior art for runtime interface systems in Python.

### Strengths

- long-lived and proven interface ecosystem;
- explicit interface declarations;
- runtime verification concepts;
- adaptation and component-system patterns;
- extensive real-world use.

### Difference from Stipulate

`zope.interface` represents a separate interface system with its own declaration and implementation concepts.

Stipulate deliberately wants to remain grounded in modern Python structural typing so that the same interface declaration remains valuable to existing static tooling without requiring implementations to opt into a separate nominal/component model.

### Stipulate strategy

Study its mature interface-verification concepts, diagnostics, and ecosystem lessons.

Do not recreate its separate interface language or component architecture.

### Competitive importance

**High historical and architectural relevance.**

---

## mypy and Pyright

### Role

Mypy and Pyright are not runtime competitors. They are interoperability targets and behavioral references.

### Why they matter

A major Stipulate selling point is that interfaces remain useful to the type checkers developers already use.

Stipulate should maintain explicit conformance fixtures for both tools.

### Stipulate strategy

- no checker plugin required for the core structural-typing experience;
- record intentional disagreements;
- follow the Python typing specification as semantic authority when checker behavior differs;
- do not claim checker support for runtime-only conveniences such as class-side APIs unless actually verified.

### Competitive importance

**Critical interoperability targets.**

---

## TypedProtocol

### Role

TypedProtocol is relevant prior art showing that other developers have identified the gap between Protocol structural typing and deeper runtime signature validation.

### Assessment

It overlaps with part of Stipulate's problem statement, including runtime structural validation and method signature/type checking.

However, it is not currently treated as a strategic competitor or roadmap baseline. Stipulate should not distort its architecture or release priorities around matching a small early-stage project feature-for-feature.

### Useful lesson

Its existence means Stipulate should avoid unsupported marketing claims such as being the first Python project ever to combine protocols and runtime validation.

### Stipulate strategy

Track as prior art. Reevaluate if ecosystem adoption or technical scope changes materially.

### Competitive importance

**Low strategic importance; relevant prior art.**

---

## Older interface/enforcement libraries

Projects such as StrictProtocol, `implements`, `python-interface`, ABC-based enforcement patterns, and similar libraries demonstrate recurring demand for runtime interface verification.

Common approaches include:

- nominal implementation inheritance;
- decorators declaring implementation;
- exact signature comparison;
- custom interface declaration systems;
- class-definition-time enforcement.

These are useful historical references but generally do not combine the properties Stipulate is targeting: modern structural typing interoperability, deep assignability semantics, Pydantic-style validation UX, and machine-readable compiled contracts.

They should be tracked as prior art rather than treated as primary strategic competitors unless their scope or adoption changes materially.

---

## Competitive matrix

| Capability | Protocol | Pydantic | Typeguard | Beartype | zope.interface | Stipulate target |
| --- | --- | --- | --- | --- | --- | --- |
| Structural interface typing | Excellent | No | Uses typing system | Uses typing system | Different interface model | Excellent |
| Complete interface runtime validation | Shallow | No | Adjacent/partial | Adjacent | Yes, own model | Core purpose |
| Callable assignability semantics | Static only | N/A | Not core interface abstraction | General typing focus | Different semantics | Core requirement |
| Pydantic-style structured errors | No | Excellent | Runtime-check errors | Rich runtime errors | Interface errors | Core requirement |
| Compiled interface metadata | No | Model-centric | No interface model | Type-hint machinery | Interface metadata | Core requirement |
| Interface schema/tooling potential | No | JSON Schema | No | No interface schema focus | Own metadata | Planned |
| Existing checker interoperability | Native | Model typing | Native annotations | Native annotations | Separate model | Required |
| Generic interface specialization | Static | Generic models | Runtime typing | Broad typing | Own model | Planned rigorous support |

The table is conceptual rather than a claim that every library has uniform behavior across every Python version and typing construct. Detailed feature claims should be verified before being used in public marketing.

## Stipulate's defensible position

Stipulate should aim to own this specific combination:

> Standard Python structural typing + deep runtime interface assignability + Pydantic-quality validation ergonomics.

No single competitive axis is sufficient by itself.

- Protocol already owns static structural typing.
- Beartype and Typeguard already own broad runtime typing territory.
- Pydantic already sets the validation UX standard.
- zope.interface already demonstrates a mature runtime interface ecosystem.

Stipulate's opportunity is to combine the relevant strengths around **complete structural interface contracts** without forcing developers into a parallel interface language.

## What Stipulate should not become

Stipulate should not become:

- a replacement static type checker;
- a general function instrumentation framework;
- an arbitrary runtime type-checking library competing on annotation count;
- a dependency injection framework;
- a nominal interface system;
- a wrapper/proxy framework by default;
- a custom alternative to Python's typing specification.

These boundaries protect the package from expanding into mature markets where its specialization would be lost.

## Strategic quality bars

### Correctness

Python's typing specification is the primary semantic authority for assignability.

### Static interoperability

Mypy and Pyright are mandatory compatibility targets for the core API.

### Runtime interface validation

Stipulate should provide materially deeper guarantees than `@runtime_checkable`.

### Developer experience

Pydantic is the benchmark for API clarity, structured diagnostics, adapters, metadata, and documentation quality.

### Runtime typing implementation

Typeguard and Beartype are important sources of lessons around difficult annotation behavior, but Stipulate should remain interface-specialized.

### Runtime interface history

`zope.interface` is important prior art for understanding mature interface systems without dictating Stipulate's declaration model.

## Competitive monitoring

Reevaluate this document before major releases and when any of the following occurs:

- Python materially expands runtime Protocol validation;
- the typing specification adds runtime-oriented interface semantics;
- Pydantic adds first-class structural interface validation;
- Typeguard or Beartype introduces a compiled complete-interface contract abstraction;
- a dedicated interface-validation package achieves meaningful adoption;
- checker capabilities make Stipulate's current `Interface` bridge or class-side typing workaround obsolete.

Competition should influence priorities when it reveals user expectations or technical lessons, but Stipulate's roadmap should remain driven by correctness and its defined product scope.