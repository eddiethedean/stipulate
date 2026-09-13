# Public Interface Model

## Planned 0.1 API

Use standard Protocol declarations and a reusable contract object:

```python
from typing import Protocol
from stipulate import Contract

class Storage(Protocol):
    def read(self, key: str) -> bytes | None: ...

storage_contract = Contract(Storage)
storage = storage_contract.validate(candidate)
result = storage_contract.check(candidate)
```

`Storage` remains the type used in annotations. `storage_contract` is the runtime contract. Do not overwrite the Protocol name with the contract instance in examples.

The constructor uses `TypeForm[T]` to preserve the relationship between the supplied declaration and the returned `T`; see STATIC_TYPING.md. It accepts only supported Protocol declarations at runtime in 0.1, even though TypeForm can represent many other type expressions.

## Construction

```python
storage_contract = Contract(Storage, annotations="trusted")
```

Construction compiles the requirement eagerly and raises `ContractDefinitionError` for an invalid, unresolvable, or unsupported requirement. `annotations="raw"` avoids requesting annotation evaluation; unresolved required annotations remain definition errors. Neither setting is a sandbox.

`Contract(Storage, refresh=True)` explicitly recompiles a changed requirement; retained contracts keep their old snapshots. Advanced `globalns` and `localns` mappings support annotations whose local names cannot otherwise be recovered.

A contract captures an immutable requirement snapshot. There is no candidate-specific state and no per-contract strictness setting. Strictness is an enforcement decision at each validation call.

## Validate

```python
storage = storage_contract.validate(candidate)
storage = storage_contract.validate(candidate, strict=False)
```

Strict is the default. Successful validation returns the original candidate, typed as `Storage`. A failed policy decision raises `ContractError`. Permissive validation tolerates only unknown type evidence with the allowlisted reasons in CONTRACT_ENGINE.md; it does not establish complete compatibility.

## Check

```python
result = storage_contract.check(candidate)
```

Candidate mismatches and supported introspection limitations become evidence rather than `ContractError`. Contract-definition failures, invalid API arguments, cancellation, and unexpected internal defects are not disguised as candidate results.

| Public observation | Meaning |
| --- | --- |
| `result.status` | `COMPATIBLE`, `INCOMPATIBLE`, or `UNKNOWN` |
| `result.compatible` | True only for `COMPATIBLE` |
| `bool(result)` | Exactly `result.compatible` |
| `result.complete` | Every applicable requirement has a conclusive outcome; failure can be complete |
| `result.errors()` | Incompatible findings only |
| `result.unknowns()` | Unknown findings only |
| `result.evidence` | All findings, including established facts |
| `result.accepted(strict=False)` | Explicit enforcement-policy decision; does not alter status |

`check()` has no strictness argument: metadata findings do not depend on the caller's willingness to tolerate them. `accepted()` defaults to `strict=True` just like `validate()`.

## Readable results

`print(result)` renders a plain-text explanation from the existing evidence. `repr(result)` shows a compact status/completeness/finding summary; `repr(contract)` identifies the declared interface. Rendering does not recheck the candidate, call its repr, print implicitly, or alter enforcement policy.

The [experience specification](EXPERIENCE_DESIGN.md) defines wording, repair guidance, and all result states. Most users need validate(), check(), and print(result); advanced evidence and configuration are introduced as needed.

## Contract representation

`storage_contract.contract is storage_contract`. This identity supports eventual Interface delegation without introducing a second adapter concept.

The public Contract facade owns immutable internal `ContractIR`. Type-system objects and source provenance may remain available for diagnostics, but internal IR records are not a versioned interchange format or a public serialization promise in 0.1.

## Composition

```python
from typing import Protocol

class Readable(Protocol):
    def read(self, key: str) -> bytes: ...

class Writable(Protocol):
    def write(self, key: str, value: bytes) -> None: ...

class Storage(Readable, Writable, Protocol):
    pass
```

The explicit Protocol base is required to preserve structural typing. A subclass without it is an ordinary class, not a new structural interface. Runtime metaclass manipulation cannot change the static checker's interpretation.

Overrides must satisfy inherited requirements. Conflicting inherited declarations produce definition diagnostics; do not silently select whichever member is easiest to validate.

## Public types in 0.1

`Contract[T]`, `CompatibilityResult`, `CompatibilityStatus`, `Evidence`, `EvidenceStatus`, `DiagnosticRecord`, `StipulateError`, `ContractError`, and `ContractDefinitionError` form the initial public model. Most users import only `Contract` and an exception when needed. Enum spelling and serialized fields follow ERROR_MODEL.md.

## Experimental Interface shorthand

```python
class Storage(Interface):
    def read(self, key: str) -> bytes | None: ...

storage = Storage.validate(candidate)
```

This design target is outside the 0.1 supported surface until OTP-001 and OTP-002 pass their gates. Experiments must demonstrate structural typing, precise class-side return types, clean member discovery, and installed-wheel behavior in both checkers. Do not ship a normal base class that makes framework methods required implementation members.

Under a Protocol-alias representation, extension must explicitly include the special base, for example `class Storage(Readable, Writable, Interface)`. That spelling still needs runtime bridge testing. Do not promise the shorter two-base spelling.

## Later operations

After separate schema and evolution gates:

```python
schema = storage_contract.schema()
fingerprint = storage_contract.fingerprint()
report = Contract(StorageV1).compare(Contract(StorageV2))
```

Schemas are Stipulate contracts, not JSON Schema. Fingerprints identify canonical semantic metadata, not compatibility. Comparison exposes `report.implementers`, `report.consumers`, `report.breaking`, and `report.complete` with the truth rules in CONTRACT_ENGINE.md.

No public `compare()`, `schema()`, `fingerprint()`, `CompatibilityReport`, or schema loader is promised for 0.1. Future `Interface` methods delegate to the same Contract operations.

## API restraint

Do not add parallel `InterfaceAdapter`, `ContractAdapter`, `model_validate`, or `validate_python` APIs. Free functions are internal primitives unless a future documented need justifies a public operation. Avoid clever operators, implicit construction/coercion, and redundant testing helpers.
