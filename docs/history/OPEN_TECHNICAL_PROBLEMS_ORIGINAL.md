# Historical technical-problem register

Archived on 2026-09-12 to preserve the original problem statements. This file is historical evidence, not current policy, API, or release scope. Its API names, prototype statuses, and release gates are superseded by ../DESIGN_DECISIONS.md and ../OPEN_TECHNICAL_PROBLEMS.md. No historical prototype claim is a passed implementation test.

---

# Open Technical Problems

This document is the authoritative backlog of unresolved technical questions in Stipulate.

The purpose is not to list vague future features. Each item defines a concrete engineering problem, the semantics Stipulate must preserve, the acceptance criteria required before support is advertised, and the release stage that depends on it.

Statuses:

- **Open** — semantics or implementation remain unresolved.
- **Prototype** — a proof of concept exists but production behavior is not yet proven.
- **Blocked** — depends on another unresolved problem or a limitation in Python typing/runtime behavior.
- **Deferred** — intentionally outside the current release target.
- **Resolved** — decision and acceptance tests are complete; move the durable decision to `DESIGN_DECISIONS.md`.

## OTP-001 — `Interface` bridge portability

**Status:** Prototype

**Release target:** 0.1 blocker

### Problem

Stipulate wants this declaration syntax:

```python
class Repository(Interface):
    ...
```

while preserving genuine Python structural protocol behavior for static checkers and runtime introspection.

The prototype uses a split representation: static checkers see `Interface` as the special `Protocol` base while runtime machinery uses `__mro_entries__` and a custom protocol-compatible metaclass.

### Required semantics

- `class Foo(Interface):` must produce a real runtime protocol.
- Framework methods must not become protocol members.
- Structural implementations must not inherit from `Foo`.
- Mypy and Pyright must recognize ordinary structural implementations.
- Interface inheritance and multiple interface inheritance must work.
- No checker plugin may be required for the core experience.

### Open questions

- Does the bridge behave consistently across all supported CPython versions?
- Does it work on PyPy or other Python implementations we may want to support?
- Which parts rely on private `typing` implementation details?
- Can the implementation be isolated so Python-version changes affect only one compatibility module?

### Acceptance tests

- CI runs the same bridge fixtures on every supported Python version.
- Mypy and Pyright accept valid structural implementations and reject representative invalid ones.
- Runtime tests assert `_is_protocol` behavior and exact protocol-member collection.
- Multiple inheritance, inherited interfaces, and empty interfaces are covered.
- No Stipulate runtime class API appears in the candidate implementation contract.

### Dependencies

None. This is foundational.

---

## OTP-002 — Statically typed class-side API

**Status:** Blocked by current Python typing expressiveness

**Release target:** Non-blocking for 0.1; revisit continuously

### Problem

Runtime syntax such as:

```python
Repository.model_validate(candidate)
```

can be provided by the Stipulate metaclass without contaminating the protocol member set. However, current static typing cannot cleanly express both:

1. `Interface` as the special protocol-defining base through `class Foo(Interface)`, and
2. custom class-side metaclass methods on every resulting interface.

### Required semantics

The statically authoritative API remains:

```python
repo = validate(Repository, candidate)
```

and must infer `Repository` correctly.

Runtime sugar may exist:

```python
repo = Repository.model_validate(candidate)
```

but documentation must not claim checker support that does not exist.

### Open questions

- Do future Python typing features provide a clean metaclass/intersection mechanism?
- Can stubs improve the class-side experience without breaking structural typing?
- Is there value in optional checker plugins later, without making them required?

### Acceptance tests

- `validate(Foo, candidate)` has correct inferred return type in mypy and Pyright.
- Runtime `Foo.model_validate(candidate)` never becomes a required structural member.
- Documentation clearly distinguishes canonical typed API from runtime convenience API.

### Dependencies

OTP-001.

---

## OTP-003 — Callable call-shape compatibility

**Status:** Prototype

**Release target:** 0.1 blocker

### Problem

An implementation must accept every call shape permitted by the interface. Annotation compatibility alone is insufficient.

The validator must correctly compare:

- positional-only parameters;
- positional-or-keyword parameters;
- keyword-only parameters;
- parameter names where keyword calls are allowed;
- defaults;
- extra required parameters;
- `*args`;
- `**kwargs`;
- bound method normalization.

### Required semantics

Compatibility must be deterministic and based on callable assignability, not heuristic generation of a few sample calls.

### Open questions

- What normalized internal representation makes all legal call shapes explicit without combinatorial explosion?
- How should builtins or extension functions with incomplete signatures be handled?
- What should permissive mode do when `inspect.signature()` cannot provide enough information?

### Acceptance tests

- Exhaustive positive/negative fixtures for every parameter-kind interaction.
- Property/fuzz tests generate random signatures and verify invariants.
- Extra optional implementation parameters are allowed where safe.
- Extra required implementation parameters are rejected.
- Keyword-only and positional-only edge cases match Python typing semantics.

### Dependencies

OTP-004 for type compatibility of parameters and returns.

---

## OTP-004 — Runtime type assignability engine

**Status:** Prototype

**Release target:** 0.1 blocker for core supported forms

### Problem

Stipulate must validate type compatibility rather than annotation equality.

For callables:

- implementation parameter annotations are checked contravariantly;
- implementation return annotations are checked covariantly.

The assignability engine must eventually handle Python typing constructs consistently with the typing specification.

### Required semantics for 0.1

Correct support for:

- identity;
- `Any`;
- missing annotations under permissive/strict policy;
- `None`;
- ordinary class/subclass relationships;
- PEP 604 and `typing.Union` unions;
- `Literal`;
- `Annotated` underlying type while retaining metadata;
- explicitly supported generic containers with known variance.

Unsupported forms must never silently fall back to annotation equality.

### Open questions

- What normalized representation should the engine use?
- How should `Any` behave differently in permissive and strict modes?
- Which generic origins can be supported safely in the initial release?
- How do we avoid encoding checker-specific extensions as Python semantics?

### Acceptance tests

- A specification-oriented assignability corpus.
- Directionality tests proving contravariant parameters and covariant returns.
- Explicit unsupported diagnostics for unknown constructs.
- Intentional mypy/Pyright disagreements are recorded rather than hidden.

### Dependencies

OTP-010 for checker parity policy.

---

## OTP-005 — Annotation resolution and forward references

**Status:** Open

**Release target:** 0.1 blocker for common cases; expanded in 0.x

### Problem

Runtime annotations may be strings or otherwise require contextual resolution because of:

- `from __future__ import annotations`;
- explicit forward references;
- nested classes;
- imported aliases;
- recursive definitions;
- local scopes.

`inspect.signature()` alone does not provide resolved semantic types.

### Required semantics

- Compilation uses a controlled annotation-resolution layer.
- The original source annotation is retained for diagnostics.
- Resolution failures become Stipulate definition diagnostics, not unrelated raw exceptions.
- Stipulate does not execute arbitrary user code merely to resolve types.

### Open questions

- Which `globalns` and `localns` sources are safe and reliable?
- How should function-local interface definitions be handled?
- When should unresolved references be a definition error versus an unsupported-type diagnostic?
- How should recursive aliases be represented without infinite recursion?

### Acceptance tests

- Future annotations.
- Same-module and cross-module forward references.
- Nested interfaces and nested implementation types.
- Unresolvable names produce stable diagnostics.
- Recursive structures do not recurse indefinitely.

### Dependencies

OTP-004 and OTP-013.

---

## OTP-006 — Generic interface specialization and `TypeVar` binding

**Status:** Open

**Release target:** Phase 3 / pre-1.0

### Problem

Generic interfaces require more than recognizing a parameterized alias. Stipulate must determine concrete bindings and enforce them consistently across every member.

Example:

```python
T = TypeVar("T")

class Repository(Interface, Generic[T]):
    def get(self, key: str) -> T: ...
    def save(self, value: T) -> None: ...
```

For `Repository[User]`, every use of `T` must specialize to `User`.

### Open questions

- How are bindings recovered from `Repository[User]` at runtime?
- How is `T` handled when an unspecialized `Repository` is validated?
- What if separate members imply incompatible bindings for the same variable?
- How do bounded and constrained `TypeVar`s behave?
- How are inherited generic interfaces specialized?
- How are multiple type variables substituted recursively through nested annotations?

### Required semantics

- Specialization happens before candidate validation.
- No silent erasure of type arguments.
- A single coherent binding environment is used throughout a compiled interface.

### Acceptance tests

- Single and multiple `TypeVar`s.
- Bound and constrained variables.
- Repeated `T` across parameters/returns/members.
- Conflicting inferred bindings.
- Generic inheritance.
- Specialized and intentionally unsupported unspecialized forms.

### Dependencies

OTP-004 and OTP-007.

---

## OTP-007 — Generic variance

**Status:** Open

**Release target:** Phase 3 / pre-1.0

### Problem

Parameterized generic types are not uniformly covariant. Mutable abstractions are commonly invariant, consumers can be contravariant, and Python 3.12+ can infer variance for type parameters.

### Open questions

- How will explicit covariance/contravariance be read at runtime?
- How will Python 3.12+ inferred variance be represented?
- Which builtin and standard-library generic origins have known variance?
- How should user-defined generic classes be handled if variance metadata is incomplete?

### Required semantics

Stipulate must never assume covariance merely because two generic origins match.

### Acceptance tests

- Covariant producer examples.
- Contravariant consumer examples.
- Invariant mutable-container examples.
- Explicit versus inferred variance fixtures.
- Conservative unsupported behavior when variance cannot be established.

### Dependencies

OTP-006 and OTP-004.

---

## OTP-008 — Overload-set validation

**Status:** Open

**Release target:** Phase 4 / pre-1.0 if advertised

### Problem

An interface may define multiple `@overload` signatures while the candidate exposes one runtime implementation signature.

Example:

```python
class Parser(Interface):
    @overload
    def parse(self, value: bytes) -> BinaryResult: ...

    @overload
    def parse(self, value: str) -> TextResult: ...
```

### Open questions

- Must the implementation be assignable to every overload individually?
- How are overlapping overloads treated?
- What runtime overload metadata is reliably available?
- How do `.pyi`-only overload definitions affect runtime validation?
- What happens when an implementation is broader than the overload set but still safely supports all calls?

### Required semantics

No overload support is advertised until Stipulate can prove that every interface-supported call is safe against the candidate.

### Acceptance tests

- Disjoint overloads.
- Overlapping overloads.
- Broad implementation satisfying multiple overloads.
- Missing overload coverage.
- Overloads with different return types.
- Missing runtime metadata produces a clear unsupported/definition diagnostic.

### Dependencies

OTP-003 and OTP-004.

---

## OTP-009 — Advanced callable typing

**Status:** Deferred

**Release target:** Phase 4

### Problem

`ParamSpec`, `Concatenate`, complex `Callable` forms, `TypeVarTuple`, and `Unpack` model parameter packs that cannot be reduced to ordinary fixed signatures without losing semantics.

### Open questions

- How should `ParamSpec` bindings be represented in compiled metadata?
- How does `Concatenate` compose with actual inspected call signatures?
- How are variadic type parameters substituted?
- Which of these forms have sufficient runtime metadata to validate reliably?

### Acceptance tests

Each construct requires its own typing-spec fixture suite before support is claimed.

### Dependencies

OTP-003, OTP-004, OTP-006.

---

## OTP-010 — Checker parity and disagreement policy

**Status:** Open

**Release target:** 0.1 blocker for core syntax

### Problem

Stipulate should align with Python's typing specification, while mypy and Pyright may disagree with each other or implement checker-specific extensions.

### Required policy

Precedence:

1. Python typing specification where semantics are defined.
2. Intentional Stipulate runtime policy where runtime information differs from static information.
3. Checker-specific compatibility accommodations only when they do not contradict the language model.

A checker disagreement must be explicit, tested, and documented.

### Open questions

- Where do mypy and Pyright materially differ for protocol/callable cases Stipulate supports?
- When is compatibility with both more valuable than strict interpretation of an underspecified rule?
- How are version-specific checker behavior changes tracked?

### Acceptance tests

Maintain `typing_tests/` fixtures with expected mypy, Pyright, and Stipulate outcomes for supported cases.

### Dependencies

OTP-001 and OTP-004.

---

## OTP-011 — Class validation versus instance validation

**Status:** Open

**Release target:** 0.x; instance semantics required for 0.1

### Problem

Instance validation can observe members created by `__init__`; class validation cannot reliably infer every runtime instance attribute.

The package must distinguish:

```python
validate(InterfaceType, instance)
```

from any future API like:

```python
validate_class(InterfaceType, ImplementationClass)
```

### Open questions

- Which members may safely be validated from a class without instantiation?
- How should annotations-only attributes be treated?
- How do `__slots__`, dataclasses, attrs classes, ORM instrumentation, and generated fields participate?
- Should class validation be intentionally weaker and return an incomplete/preflight result?

### Required semantics

0.1 instance validation must not claim that class-level introspection proves instance state that is only established during construction.

### Acceptance tests

- `__init__`-created attributes.
- class attributes.
- slots.
- dataclasses.
- annotation-only members.
- explicit documentation of differences between class and instance validation.

### Dependencies

OTP-012.

---

## OTP-012 — Attributes, properties, and descriptor semantics

**Status:** Open / partially prototyped

**Release target:** 0.1 for attributes/properties; expanded in Phase 2

### Problem

Python exposes several different member forms with different read/write semantics:

- plain instance attributes;
- class attributes;
- read-only properties;
- writable properties;
- custom descriptors;
- `cached_property`;
- dynamic attributes.

A current runtime value matching a type does not prove the declaration is safely writable.

### Required semantics

Stipulate must internally distinguish at least:

- readable member;
- writable member;
- read-only property;
- writable property.

Declaration compatibility and current-value validation remain separate concepts.

### Open questions

- How are custom descriptor setter/getter annotations recovered?
- How should data descriptors and non-data descriptors differ?
- Does permissive mode accept a dynamically supplied member when declaration compatibility cannot be proven?

### Acceptance tests

- plain attributes;
- class attributes;
- read-only/writable properties;
- custom descriptor fixtures;
- `cached_property`;
- mismatch between current value and declared writable contract.

### Dependencies

OTP-011 and OTP-014.

---

## OTP-013 — Definition errors versus candidate validation errors

**Status:** Open

**Release target:** 0.1 blocker

### Problem

Two fundamentally different failures must not be conflated:

1. the interface itself cannot be compiled or interpreted correctly;
2. the candidate does not satisfy a valid interface.

Examples of definition failures include unresolved annotations, unsupported declarations in strict mode, malformed metadata, or impossible interface constructs.

### Required semantics

Stipulate should provide a distinct definition/compilation error path from `InterfaceValidationError` or otherwise make the distinction unambiguous in structured diagnostics.

### Open questions

- Separate exception class versus shared base class with phase metadata?
- Are unsupported constructs definition errors or validation errors when only encountered for a particular specialization?
- Which failures should be cached with the compiled interface?

### Acceptance tests

- unresolved forward reference;
- unsupported type construct;
- malformed interface declaration;
- normal candidate mismatch;
- callers can distinguish definition failure without parsing strings.

### Dependencies

OTP-005 and OTP-015.

---

## OTP-014 — Dynamic members and introspection uncertainty

**Status:** Open / partially prototyped

**Release target:** 0.x; explicit 0.1 policy required

### Problem

Objects using `__getattr__`, `__getattribute__`, proxies, ORM instrumentation, extension types, or runtime monkey-patching may expose members that static inspection cannot prove.

### Required semantics

Stipulate must distinguish:

- member proven by declaration/introspection;
- member present on the current instance;
- member dynamically claimed but not statically inspectable.

Strict mode should require stronger proof than permissive mode.

### Open questions

- Is successful `getattr` sufficient evidence for readable attributes in permissive mode?
- How should callable dynamic members be validated when no inspectable signature exists?
- Should diagnostics include a confidence/proof category?

### Acceptance tests

- `__getattr__` dynamic attribute.
- dynamic callable.
- proxy object.
- extension/builtin callable with unavailable signature.
- strict and permissive outcomes are explicit.

### Dependencies

OTP-003 and OTP-012.

---

## OTP-015 — Decorators and signature recovery

**Status:** Open

**Release target:** 0.1 hardening

### Problem

Decorators can preserve, replace, or obscure a callable signature. Runtime sources include:

- `__wrapped__`;
- `__signature__`;
- the visible wrapper signature;
- generated callables with incomplete metadata.

### Open questions

- What precedence should Stipulate use among `__signature__`, unwrapped signature, and wrapper signature?
- When is unwrapping semantically wrong because the wrapper intentionally changes the public contract?
- How many unwrap levels are safe?

### Required semantics

Stipulate validates the externally callable contract, not blindly the original undecorated implementation.

### Acceptance tests

- `functools.wraps` preserving signature.
- explicit `__signature__` override.
- decorator that intentionally adds/removes parameters.
- stacked decorators.
- wrapper cycle/malformed metadata protection.

### Dependencies

OTP-003.

---

## OTP-016 — Async, generators, and awaitable semantics

**Status:** Partially prototyped

**Release target:** 0.1 for sync/async mismatch; later expansion

### Problem

`async def` syntax is only one asynchronous contract. Python also has:

- sync functions returning `Awaitable[T]`;
- async generators;
- sync generators;
- async context managers;
- callable objects whose `__call__` is async.

### Open questions

- Does the interface require syntactic `async def`, semantic awaitability, or annotation compatibility?
- How should async generators differ from coroutines?
- Should callable objects be normalized through `__call__`?

### Required semantics for 0.1

A declared `async def` interface method must not silently accept an ordinary synchronous method merely because its return annotation resembles an awaitable, unless that behavior is explicitly designed and tested.

### Acceptance tests

- sync vs async mismatch.
- async callable objects.
- later: generator and context-manager matrices.

### Dependencies

OTP-003 and OTP-004.

---

## OTP-017 — Nested protocols as annotation types

**Status:** Open

**Release target:** Phase 2

### Problem

An interface member may use another protocol/interface as a parameter or return annotation.

Example:

```python
class Store(Interface):
    def save(self, serializer: Serializer) -> None: ...
```

Stipulate must decide whether assignability of `Serializer` is evaluated purely as a typing annotation relationship or invokes deeper Stipulate structural validation.

### Required semantics

Type assignability and recursive candidate validation must not be accidentally conflated.

### Open questions

- Does nested protocol assignability rely on normal subclass/protocol typing semantics only?
- Is there an opt-in mode for recursively validating runtime values?
- How are recursive protocol references prevented from causing validation cycles?

### Acceptance tests

- nested protocol parameter/return annotations.
- mutually recursive protocols.
- normal class satisfying a nested structural protocol.
- no unbounded recursive validation.

### Dependencies

OTP-004 and OTP-005.

---

## OTP-018 — `Self`

**Status:** Open

**Release target:** Phase 4

### Problem

`Self` depends on the enclosing interface/class and may appear in return types, parameters, classmethods, and inherited interfaces.

### Open questions

- What does `Self` bind to when validating a structural implementation that does not inherit from the interface?
- Should `Self` represent the candidate concrete class, the interface type, or an assignability relationship between them?
- How does inheritance change the binding?

### Acceptance tests

Require typing-spec examples plus structural implementation cases before support is advertised.

### Dependencies

OTP-004 and OTP-006.

---

## OTP-019 — Typed `**kwargs`, `TypedDict`, and `Unpack`

**Status:** Deferred

**Release target:** Phase 4

### Problem

Modern Python typing can use `Unpack[TypedDict]` to describe keyword parameter sets precisely. This affects both call shape and type compatibility.

### Open questions

- How are required versus optional keys mapped into callable compatibility?
- How do `total=False` and `Required`/`NotRequired` affect assignability?
- How does `**kwargs: Unpack[T]` interact with an ordinary `**kwargs` implementation?

### Acceptance tests

Typing-spec-driven fixture matrix before support is advertised.

### Dependencies

OTP-003, OTP-004, OTP-009.

---

## OTP-020 — Mutation and cache invalidation

**Status:** Open

**Release target:** 0.1 policy; advanced behavior can be deferred

### Problem

Python classes can be monkey-patched after an interface has been compiled or a candidate has been validated.

Stipulate intends validation to be point-in-time, but caches must not accidentally promise stronger immutability than Python provides.

### Required semantics

- A successful validation does not guarantee future conformance after mutation.
- Compiled interface metadata is cached because interface definitions are expected to be stable.
- Cache behavior under deliberate mutation must be documented.

### Open questions

- Do we ever attempt automatic invalidation if an interface class changes?
- Should there be an explicit `clear_cache(interface=None)` API?
- Can weak references prevent stale class retention without expensive mutation tracking?

### Acceptance tests

- weak-reference lifecycle.
- cache clear behavior if exposed.
- documented result when an interface is monkey-patched after compilation.
- candidate mutation after validation has no hidden proxy enforcement.

### Dependencies

OTP-021.

---

## OTP-021 — Compiled metadata caching and thread safety

**Status:** Prototype

**Release target:** 0.1 blocker

### Problem

Compilation performs expensive introspection, annotation resolution, signature normalization, and member classification. The result should be immutable and reusable across validation calls.

### Required semantics

- compiled metadata contains no candidate-specific state;
- cache does not keep dead interface classes alive unnecessarily;
- concurrent validation is safe;
- failed compilation behavior is deterministic.

### Open questions

- WeakKeyDictionary versus another weak-reference strategy?
- Should compilation be protected by per-interface locks, a global lock, or idempotent duplicate work?
- Are failed definition compilations cached?

### Acceptance tests

- warm validation reuses the same compiled contract.
- interface classes can be garbage-collected.
- concurrent compilation/validation stress test.
- no mutable shared candidate state.

### Dependencies

OTP-005 and OTP-013.

---

## OTP-022 — Error-code and diagnostic stability

**Status:** Open

**Release target:** 0.1 initial contract; 1.0 stability guarantee

### Problem

Structured errors are part of Stipulate's public value. Frameworks and CI systems may depend on error codes and locations.

### Required semantics

Every diagnostic should have stable machine-readable fields such as:

```python
{
    "loc": ("save", "value"),
    "type": "parameter_type",
    "msg": "Implementation parameter type is too narrow",
    "expected": ...,
    "actual": ...,
}
```

### Open questions

- Which fields are guaranteed from 0.1 versus 1.0?
- How are nested causes represented?
- How are unsupported features distinguished from invalid implementations?
- Is human-readable wording semver-stable or only machine-readable codes?

### Acceptance tests

- deterministic error ordering.
- multi-error aggregation.
- stable locations and codes.
- definition errors and candidate errors are distinguishable.

### Dependencies

OTP-013.

---

## OTP-023 — Versioned interface schema

**Status:** Open

**Release target:** Phase 5

### Problem

`interface_schema()` should eventually expose machine-readable compiled interface metadata, but a schema format becomes a compatibility surface of its own.

### Open questions

- JSON-serializable versus Python-native schema representation?
- How are arbitrary Python types represented?
- How are signatures, variance, overloads, generics, and unsupported constructs encoded?
- How is schema versioning declared?
- Can schemas be compared for compatibility between interface versions?

### Required semantics

Do not stabilize a schema accidentally through an undocumented dictionary shape.

### Acceptance tests

- explicit schema version.
- deterministic serialization.
- round-trip tests if deserialization is supported.
- schema changes follow a documented compatibility policy.

### Dependencies

Most compilation/type-system problems; especially OTP-004, OTP-006, OTP-008.

---

## OTP-024 — Performance boundaries and benchmarking

**Status:** Open

**Release target:** Benchmark baseline before beta; hard guarantees by 1.0 if justified

### Problem

Deep runtime interface validation is inherently more expensive than member-presence checks. Stipulate must prevent annotation resolution and normalization costs from dominating repeated validation.

### Open questions

- What is an acceptable cold-compilation cost?
- What is an acceptable warm-validation overhead for typical interfaces?
- Which operations dominate runtime cost?
- Should strict mode have a separate performance target?

### Required semantics

Performance work must not weaken correctness or silently skip validation.

### Acceptance tests

Benchmarks for:

- cold compilation;
- warm validation;
- interfaces with many members;
- deep annotation trees;
- valid and invalid candidates;
- strict vs permissive modes.

### Dependencies

OTP-021.

---

## OTP-025 — Supported Python implementations and versions

**Status:** Open

**Release target:** 0.1 explicit matrix; 1.0 stable policy

### Problem

Stipulate interacts closely with `typing`, introspection, signatures, and protocol runtime behavior, all of which evolve between Python versions.

### Open questions

- Minimum supported Python version?
- CPython-only initially, or PyPy too?
- How quickly are newly released Python versions added?
- Which compatibility shims may use `typing_extensions`?

### Required semantics

Every advertised Python version must run the runtime test suite and checker fixtures in CI.

### Acceptance tests

Support matrix in CI and documentation; no version is advertised solely because the package imports successfully.

### Dependencies

OTP-001 and OTP-005.

---

## Release gates

### 0.1 must resolve or explicitly freeze policy for

- OTP-001 — Interface bridge portability
- OTP-003 — callable call-shape compatibility
- OTP-004 — core runtime assignability
- OTP-005 — common annotation resolution
- OTP-010 — checker parity policy
- OTP-012 — basic attribute/property semantics
- OTP-013 — definition vs candidate errors
- OTP-015 — decorator/signature recovery policy
- OTP-016 — basic async semantics
- OTP-020 — mutation/cache policy
- OTP-021 — cache/thread safety
- OTP-022 — initial error contract
- OTP-025 — Python support matrix

### Pre-1.0 correctness expansion

- OTP-006 — generic specialization
- OTP-007 — generic variance
- OTP-008 — overloads, if advertised
- OTP-017 — nested protocols
- OTP-018 — `Self`, if advertised
- OTP-023 — versioned schema if public before 1.0
- OTP-024 — benchmark baseline and performance policy

### Explicitly advanced/deferred until spec-driven implementation exists

- OTP-009 — advanced callable typing
- OTP-019 — typed `**kwargs` / `Unpack[TypedDict]`

## Maintenance rule

When an open problem is solved:

1. add or update conformance tests;
2. record the durable architectural decision in `DESIGN_DECISIONS.md`;
3. update the relevant focused design document;
4. mark the OTP item **Resolved** with the release/version that resolved it;
5. never remove the historical problem statement unless it is superseded by an ADR or equivalent permanent design record.

Stipulate should prefer an explicit unsupported diagnostic over a superficially working implementation whose semantics are not proven.
