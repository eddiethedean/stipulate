# Type System and Assignability

## Principle

Stipulate validates compatibility, not annotation equality.

The runtime engine should mirror Python typing assignability semantics wherever runtime information is sufficient. It must not invent alternative variance rules simply because they are easier to implement.

## Callable compatibility

An implementation method must accept every call permitted by the interface and return values compatible with the interface return type.

This implies:

- parameter types are checked contravariantly;
- return types are checked covariantly;
- parameter kinds matter;
- defaults matter;
- keyword names matter where calls may use keywords;
- extra required parameters can make an implementation incompatible;
- variadic parameters can broaden compatibility.

Example:

```python
class Animal: ...
class Dog(Animal): ...


class Handler(Interface):
    def handle(self, value: Dog) -> Animal: ...


class Good:
    def handle(self, value: Animal) -> Dog:
        ...
```

`Good` is compatible because it accepts a broader parameter type and returns a narrower result type.

The reverse is not valid.

## Parameter shape

The validator must normalize and compare:

- positional-only parameters;
- positional-or-keyword parameters;
- keyword-only parameters;
- defaults;
- `*args`;
- `**kwargs`.

The implementation must support all valid call shapes implied by the interface declaration.

Avoid heuristic call generation as the final production algorithm where a deterministic parameter-compatibility algorithm is possible.

## Missing annotations and `Any`

Stipulate needs two explicit modes.

### Permissive mode

Default behavior should align with gradual typing. Missing implementation annotations may behave as `Any` where appropriate.

```python
validate(Service, candidate)
```

### Strict mode

Strict mode should require sufficient implementation annotations to prove compatibility when the interface declares types.

```python
validate(Service, candidate, strict=True)
```

Strictness must be documented as a Stipulate policy layered on top of Python typing rather than presented as standard static-checker behavior.

## Initial supported type forms

The first production milestone should handle well-tested semantics for:

- `Any`;
- `None` / `NoneType`;
- normal classes and subclass relationships;
- unions, including PEP 604 unions;
- `Literal`;
- `Annotated` by validating the underlying type while preserving metadata;
- common parameterized containers where assignability can be implemented correctly;
- callable return and parameter annotations.

## Advanced forms

The following require dedicated design and conformance tests before being advertised as supported:

- `TypeVar` binding and constraints;
- covariance and contravariance of generic parameters;
- Python 3.12+ inferred variance;
- `Self`;
- `ParamSpec`;
- `Concatenate`;
- `TypeVarTuple`;
- `Unpack`;
- overload sets;
- complex `Callable` forms;
- typed dictionaries in `**kwargs`;
- recursive aliases;
- protocols used as nested annotation types.

Unsupported advanced constructs should produce a clear unsupported-type diagnostic in strict validation rather than silently falling back to equality or permissive acceptance.

## Generic containers

Do not assume all parameterized containers are covariant.

For example, mutable generic types are often invariant while read-only abstractions may be covariant. The assignability engine must have explicit variance knowledge or delegate to a trusted representation where possible.

Until this is implemented rigorously, conservative rejection is safer than incorrect acceptance.

## Forward references

Annotations may be strings because of `from __future__ import annotations` or explicit forward references.

Compilation should use robust type-hint resolution with the relevant global and local namespaces. Failures should retain the original annotation and produce useful diagnostics rather than crashing compilation with unrelated exceptions.

## Type aliases

PEP 695 and legacy aliases should be normalized carefully while preserving enough source information for error messages.

## Runtime values versus declarations

Type assignability of a member declaration is distinct from runtime validation of the current value.

Stipulate should not conflate:

```text
implementation annotation compatible with interface annotation
```

and:

```text
current instance value is an instance of the expected runtime type
```

Some typing constructs have no direct runtime `isinstance` meaning. These concerns should remain separate internally even if a high-level validation mode requests both.

## Checker parity target

For cases where runtime metadata is sufficient, Stipulate should maintain test fixtures that compare expected outcomes with Pyright and mypy.

Perfect parity is not always possible because static and runtime information differ, but disagreements should be intentional, documented, and tested.
