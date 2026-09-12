# Pydantic Integration

## Status

**Post-1.0 optional integration.**

Pydantic must not be a hard dependency of Stipulate core.

## Principle

> **Stipulate owns structural contracts. Pydantic can enhance value validation and serialization where those concerns naturally intersect.**

The two projects solve complementary problems:

- Pydantic validates data and runtime values.
- Stipulate validates and evolves object/interface contracts.

Integration should preserve that boundary rather than coupling the two engines.

## Packaging

Core installation remains independent:

```text
pip install stipulate
```

Pydantic-specific capabilities may be exposed through an optional extra:

```text
pip install "stipulate[pydantic]"
```

and a clearly isolated integration namespace where useful:

```python
from stipulate.pydantic import ...
```

Installing or not installing Pydantic must not change Stipulate's core contract compatibility semantics.

## Natural integration points

### Pydantic models in interface signatures

Pydantic models are ordinary Python types and should compose naturally with Stipulate interfaces:

```python
from pydantic import BaseModel
from stipulate import Interface


class User(BaseModel):
    id: int
    name: str


class Repository(Interface):
    def get(self, id: int) -> User | None: ...
    def save(self, user: User) -> None: ...
```

This requires no special runtime coupling for the basic contract declaration. Post-1.0 documentation should explicitly show the pairing.

### Optional current-value validation

Stipulate's core contract engine reasons about member/type compatibility. A separate optional mode may validate current instance attribute/property values using Pydantic `TypeAdapter` where appropriate.

Example conceptual API, not frozen:

```python
Service.validate(candidate, values="pydantic")
```

or an integration-specific method/helper under `stipulate.pydantic`.

The API should be chosen only after the core distinction between declaration compatibility and current-value validation is stable.

Pydantic value validation must not be mistaken for proof of callable/interface assignability.

### Serializable result/report models

Stipulate's `CompatibilityResult`, `CompatibilityReport`, `Evidence`, and contract schema data may have optional Pydantic representations or export helpers for users building APIs and tooling.

Possible benefits:

- JSON serialization;
- FastAPI response models;
- validation of externalized Stipulate reports;
- easier logging/event pipelines;
- generated JSON Schema for the **report data**, distinct from the Stipulate contract schema itself.

Core result objects should not need to inherit from `BaseModel`.

### FastAPI integration

FastAPI is a natural demonstration of the boundary:

```python
class PaymentRequest(BaseModel):
    amount: Decimal


class PaymentProvider(Interface):
    async def charge(self, request: PaymentRequest) -> PaymentResult: ...
```

Pydantic/FastAPI validate request and response data while Stipulate validates a dynamically loaded or dependency-injected provider implementation.

Post-1.0 integration work may include documentation and small helpers if real use cases justify them. Stipulate should not become a dependency injection framework.

### Contract/report tooling

Where Stipulate schemas, snapshots, or compatibility reports need to be consumed as ordinary application data, optional Pydantic models may provide a convenient typed representation.

This is an integration/export concern. The canonical Stipulate contract schema remains owned and versioned by Stipulate.

## Explicit non-goals

Pydantic integration must not:

- make Pydantic a core dependency;
- make `Interface` inherit from `BaseModel`;
- use Pydantic as Stipulate's callable assignability engine;
- delegate structural contract compatibility to `TypeAdapter`;
- change compatibility results depending on whether Pydantic is installed;
- make Stipulate contract schemas aliases for JSON Schema;
- leak Pydantic-specific metadata into the canonical core contract IR;
- force Pydantic onto downstream implementations;
- delay core releases because of Pydantic compatibility work.

## Dependency direction

The architecture must remain:

```text
stipulate core
      ↑
stipulate.pydantic
```

not:

```text
stipulate core → pydantic
```

The integration layer consumes stable Stipulate APIs.

## Versioning

Pydantic compatibility should have its own documented support matrix once the integration ships.

A breaking change in Pydantic must not force a breaking change to Stipulate's core contract format or semantics.

## Release gate

Do not begin first-class Pydantic integration until after 1.0 unless a small documentation-only example is useful earlier.

Before implementation:

1. core `Contract`, `CompatibilityResult`, and schema APIs must be stable;
2. declaration compatibility versus current-value validation must be formally settled;
3. benchmarks must show optional value validation does not accidentally become part of ordinary contract checks;
4. integration APIs must demonstrate meaningful ergonomics over users directly calling Pydantic themselves.

## Success criterion

Pydantic users should feel that Stipulate fits naturally beside Pydantic without either project pretending to solve the other's problem.