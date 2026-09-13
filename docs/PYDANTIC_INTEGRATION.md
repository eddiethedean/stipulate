# Pydantic Integration

## Status and boundary

Optional and post-1.0. Pydantic must not be a core dependency or change core compatibility results when installed. The integration layer consumes stable Stipulate APIs; Stipulate does not depend on it.

Pydantic can validate values and serialize application data. Stipulate compares structural declarations and explains compatibility. Neither engine substitutes for the other.

## Ordinary model types in signatures

A Pydantic model can appear as an ordinary nominal type in a supported Protocol signature without special coupling:

```python
from typing import Protocol
from pydantic import BaseModel
from stipulate import Contract

class User(BaseModel):
    id: int
    name: str

class Repository(Protocol):
    def get(self, id: int) -> User | None: ...

repository_contract = Contract(Repository)
```

Stipulate checks the declared nominal relationship. It does not validate model fields, instantiate User, or inspect future method results. Small examples can ship before the post-1.0 integration package.

Annotated constraints, including Pydantic PositiveInt-style aliases, do not become nominal subtypes in Stipulate. The core uses the underlying type and does not enforce constraint metadata. Do not use such aliases as examples of parameter narrowing. [Pydantic type documentation](https://pydantic.dev/docs/validation/latest/concepts/types/)

## Optional current-value checking

A later explicit integration may use TypeAdapter to inspect current attribute/property values. This is a separate operation with explicit attribute-access effects, not an implicit addition to ordinary Contract.check(). Its API is not frozen here.

Do not coerce a value and discard the replacement while returning the unchanged candidate as validated. Value checking should be non-coercing, or transformation must be a separately named operation that returns the transformed artifact. A successful value check does not prove writable declaration compatibility or future behavior.

## Report exports

Optional Pydantic representations may help users expose results through APIs, logs, or FastAPI. They consume stable core exports; core Evidence and CompatibilityResult do not inherit from BaseModel.

JSON Schema for report data is different from the versioned Stipulate contract schema. Installation of an export helper must not affect core serialization or relation results.

## Packaging and gates

Use a separate namespace and optional stipulate[pydantic] extra only once an implementation is justified. Before first-class integration:

- Core public results and relevant schema APIs are stable.
- Current-value versus declaration guarantees are settled.
- Access effects and coercion policy are tested.
- Independent version compatibility is documented.
- Examples show a meaningful improvement over directly using Pydantic.

FastAPI can serve as a later example: it validates request/response data while Stipulate checks a dynamically selected service declaration. Stipulate remains independent of dependency injection and web frameworks.
