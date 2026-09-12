# Interface Model

## Goal

The interface declaration should feel like defining a Pydantic model, but describe an object's behavioral contract instead of JSON-shaped data.

```python
from stipulate import Interface


class Repository(Interface):
    name: str

    def get(self, id: int) -> User | None: ...

    async def save(self, user: User) -> None: ...

    @property
    def ready(self) -> bool: ...
```

Implementations do not inherit from the interface:

```python
class PostgresRepository:
    name = "postgres"

    def get(self, id: int) -> User | None:
        ...

    async def save(self, user: User) -> None:
        ...

    @property
    def ready(self) -> bool:
        return True
```

## Structural semantics

Stipulate interfaces are structural. An implementation satisfies an interface based on compatible members, not inheritance.

Nominal inheritance may still be used by application code, but Stipulate must not require it.

## Member categories

The compiler should classify members explicitly.

### Instance methods

```python
class Service(Interface):
    def run(self, value: str) -> int: ...
```

Validate:

- member presence;
- callable nature;
- signature compatibility;
- parameter assignability;
- return assignability;
- sync/async compatibility.

### Async methods

```python
class Service(Interface):
    async def run(self, value: str) -> int: ...
```

An ordinary synchronous method is not compatible merely because it returns an awaitable unless Stipulate explicitly adds such a compatibility rule in a future version.

Initial behavior should prefer clear syntactic async compatibility.

### Attributes

```python
class Service(Interface):
    name: str
```

Stipulate must distinguish two questions:

1. Does the implementation declare a compatible attribute contract?
2. Does this specific instance currently contain a compatible value?

The core interface validator should primarily validate the declared/member contract. Optional value validation may inspect current values where meaningful.

### Properties

```python
class Service(Interface):
    @property
    def name(self) -> str: ...
```

A read-only property should be represented separately from a writable attribute because mutability affects assignability.

### Class methods and static methods

These should be supported deliberately rather than accidentally. Their binding behavior and first parameters differ from ordinary methods and must be normalized before compatibility checks.

## Inheritance

Interfaces may compose through normal inheritance:

```python
class Readable(Interface):
    def read(self, key: str) -> bytes: ...


class Writable(Interface):
    def write(self, key: str, value: bytes) -> None: ...


class Storage(Readable, Writable):
    pass
```

The compiler should merge inherited members, preserve overriding semantics, and detect impossible or conflicting declarations.

## Existing Protocols

Stipulate should support ordinary `typing.Protocol` classes through `InterfaceAdapter`:

```python
class ExistingRepository(Protocol):
    def get(self, id: int) -> User | None: ...


adapter = InterfaceAdapter(ExistingRepository)
adapter.validate_python(candidate)
```

This is important for adoption in mature codebases.

## Metadata API

Compiled interfaces should expose machine-readable metadata:

```python
Repository.interface_schema()
```

The schema is not JSON Schema. It should be treated as a Stipulate interface schema with a versioned format.

Example conceptual form:

```python
{
    "schema_version": 1,
    "name": "Repository",
    "members": {
        "get": {
            "kind": "method",
            "async": False,
            "parameters": [...],
            "return": "User | None",
        }
    },
}
```

Do not promise stable serialization until the schema format has an explicit versioning policy.

## Optional members

Optional interface members are useful but should not be rushed into the first release because Python `Protocol` has no direct universal optional-member syntax.

A future Stipulate-specific declaration may be introduced only if it remains clear to static type checkers or is explicitly documented as runtime-only metadata.

## Extra members

Extra implementation members are always allowed by default. Structural interfaces describe minimum required capability, not exact object shape.

A future exact-interface mode could exist for specialized cases, but it should not be the default.
