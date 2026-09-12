# Architecture

## Overview

Stipulate is organized around a small public API backed by a compiled interface model and a runtime assignability engine.

```text
User interface declaration
        |
        v
  Interface / Protocol bridge
        |
        v
   Interface compiler
        |
        +--> resolved annotations
        +--> normalized member metadata
        +--> normalized call signatures
        +--> inherited members
        |
        v
   CompiledInterface cache
        |
        v
   Validation engine
        |
        +--> member existence
        +--> callable compatibility
        +--> async compatibility
        +--> attribute/property checks
        +--> type assignability
        |
        v
 structured errors or original object
```

## Public layers

### `Interface`

`Interface` exists to provide the desired declaration syntax:

```python
class Repository(Interface):
    ...
```

The runtime implementation may use `__mro_entries__` so that a declaration receives both Stipulate runtime machinery and genuine `Protocol` behavior.

For static analysis, `Interface` should be presented as the special `Protocol` base so that normal type checkers continue to recognize subclasses structurally.

### `validate(interface, value)`

This is the statically authoritative validation API:

```python
T = TypeVar("T")

def validate(interface: type[T], value: object, *, strict: bool = False) -> T:
    ...
```

A successful call returns the original value typed as the interface.

### `InterfaceAdapter`

An adapter API should support existing plain protocols without migration:

```python
adapter = InterfaceAdapter(ExistingProtocol)
adapter.validate_python(candidate)
```

This also gives callers an explicit reusable compiled validator.

### Class-side sugar

Runtime classes may expose:

```python
Repository.model_validate(candidate)
Repository.interface_schema()
```

These methods should live on Stipulate's metaclass and must never become required protocol instance members.

Because Python's current typing model cannot fully express both the `Protocol` alias identity and custom metaclass API through the one-base syntax, the free `validate()` function remains the checker-authoritative form.

## Internal modules

A production implementation should favor focused modules:

```text
stipulate/
    __init__.py
    _interface.py
    _compile.py
    _members.py
    _signatures.py
    _assignability.py
    _annotations.py
    _errors.py
    _cache.py
    adapter.py
    config.py
```

Suggested responsibilities:

- `_interface.py`: runtime `Interface` bridge and metaclass.
- `_compile.py`: turns an interface class into `CompiledInterface`.
- `_members.py`: member classification and metadata.
- `_signatures.py`: callable normalization and call-shape compatibility.
- `_assignability.py`: type relation checks.
- `_annotations.py`: type-hint resolution and forward-reference support.
- `_errors.py`: structured error types and rendering.
- `_cache.py`: compiled contract caches.
- `adapter.py`: public `InterfaceAdapter`.
- `config.py`: strictness and future validation policies.

## Core data structures

### `CompiledInterface`

A compiled interface should be immutable or effectively immutable.

```python
@dataclass(frozen=True)
class CompiledInterface:
    interface: type
    members: tuple[CompiledMember, ...]
    config: InterfaceConfig
```

### Member kinds

Use explicit internal member types rather than dictionaries where practical:

```text
CompiledMethod
CompiledProperty
CompiledAttribute
CompiledClassMethod
CompiledStaticMethod
```

Each member should retain the original annotation objects and normalized representations needed by the validator.

## Validation lifecycle

1. Confirm the supplied interface is supported.
2. Retrieve or compile `CompiledInterface`.
3. Inspect the candidate safely.
4. Validate each required member.
5. Accumulate all independent errors rather than failing on the first mismatch.
6. Raise one `InterfaceValidationError` if errors exist.
7. Otherwise return the original candidate.

## Safety rules

Stipulate should avoid executing arbitrary implementation methods merely to determine compatibility.

Introspection may access descriptors or properties if normal `getattr` is used, which can have side effects. The implementation should prefer static inspection APIs where possible and clearly distinguish declaration inspection from optional runtime-value validation.

## Extension architecture

The core should be designed so future support for advanced typing constructs can be added through internal handlers without making the public API unstable.

Do not expose a public plugin system until the assignability semantics and internal extension points are stable.
