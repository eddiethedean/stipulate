# Design Decisions

This document records the architectural decisions that should remain stable unless new evidence justifies changing them.

## D001 — Package name: Stipulate

**Decision:** The Python package and project are named `stipulate` / Stipulate.

**Rationale:** The name describes explicit behavioral conditions and contracts without tying the project to one implementation mechanism.

---

## D002 — Use normal class syntax

**Decision:** The primary declaration form is:

```python
class Foo(Interface):
    ...
```

**Rationale:** This is the most natural analogue to Pydantic model definitions and minimizes custom syntax.

**Consequence:** Runtime machinery must preserve genuine protocol behavior while presenting `Interface` appropriately to static checkers.

---

## D003 — Preserve structural typing

**Decision:** Implementations are not required to inherit from Stipulate interfaces.

**Rationale:** The value of Python protocols is structural substitutability. Requiring nominal inheritance would weaken the product considerably.

---

## D004 — Compose with `typing.Protocol`

**Decision:** Stipulate interfaces should remain grounded in Python's protocol model rather than defining an unrelated interface system.

**Rationale:** Existing type checkers, IDEs, and annotations already understand protocols.

---

## D005 — No required mypy/Pyright plugin

**Decision:** Basic interface use must work with normal static typing tools without custom plugins.

**Rationale:** Checker compatibility is a core selling point, not an optional integration.

**Consequence:** Some runtime class-side sugar may be less precisely typed than the free validation API.

---

## D006 — `validate()` is the statically authoritative API

**Decision:**

```python
validate(Foo, candidate)
```

is the canonical API for static type inference.

**Rationale:** Current Python typing cannot fully express the custom metaclass API while also representing `Interface` as the special structural protocol base through the desired one-base syntax.

**Consequence:**

```python
Foo.model_validate(candidate)
```

may exist as runtime convenience, but documentation should not claim checker support that does not exist.

---

## D007 — Runtime API belongs on the metaclass

**Decision:** Pydantic-like class APIs such as `model_validate()` and `interface_schema()` should be implemented on Stipulate's metaclass/runtime class machinery, not as protocol members.

**Rationale:** Protocol members would become requirements for every structural implementation.

---

## D008 — Validation returns the original object

**Decision:** Successful validation returns the candidate itself.

**Rationale:** Stipulate verifies contracts; it does not need a proxy for ordinary validation.

**Consequence:** Validation is point-in-time and does not prevent later monkey-patching.

---

## D009 — Compatibility, not annotation equality

**Decision:** Type checks must implement assignability semantics.

**Rationale:** Callable parameters are contravariant and returns are covariant. Annotation equality would reject valid implementations and accept some invalid call shapes.

---

## D010 — Explicit strict and permissive modes

**Decision:** Missing implementation annotations may be allowed in default/permissive mode but must be rejected when strict validation requires proof.

**Rationale:** Python uses gradual typing, but runtime consumers sometimes need stronger guarantees.

---

## D011 — Compile once, validate many

**Decision:** Interfaces compile into cached immutable metadata.

**Rationale:** Annotation resolution and signature normalization are too expensive and complex to repeat for every candidate.

---

## D012 — Structured errors are public API

**Decision:** Validation errors expose stable structured records, not only human-readable strings.

**Rationale:** Frameworks, IDEs, CI systems, and tests need machine-readable diagnostics.

---

## D013 — Fail clearly on unsupported typing constructs

**Decision:** Stipulate must not pretend to validate advanced typing forms it does not understand.

**Rationale:** False confidence is worse than a clear limitation.

**Consequence:** Strict validation should emit `unsupported_type` or a definition error rather than silently reducing unknown forms to equality or `Any`.

---

## D014 — Static contract and current runtime value are distinct concepts

**Decision:** Internally separate declaration compatibility from current instance-value validation.

**Rationale:** A current value can match an annotation while the declared writable contract is incompatible, and many typing forms do not map directly to `isinstance` checks.

---

## D015 — Do not execute arbitrary methods to validate behavior

**Decision:** Core validation uses introspection and metadata, not behavioral method execution.

**Rationale:** Executing unknown code would introduce side effects, security concerns, nondeterminism, and argument-generation problems.

---

## D016 — Existing Protocols are first-class inputs

**Decision:** `InterfaceAdapter` supports ordinary existing `Protocol` classes.

**Rationale:** Mature codebases should be able to adopt runtime validation without rewriting every protocol.

---

## D017 — Typing specification is the semantic source of truth

**Decision:** Python's typing specification is the primary reference for assignability semantics.

**Rationale:** Mypy and Pyright are important compatibility targets but can disagree or implement extensions. Stipulate should not blindly encode checker-specific behavior as language semantics.
