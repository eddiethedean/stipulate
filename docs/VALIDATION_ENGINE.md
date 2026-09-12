# Validation Engine

## Objective

The validation engine determines whether a candidate object satisfies a compiled Stipulate interface and returns the original object on success.

```python
validated = validate(MyInterface, candidate)
assert validated is candidate
```

## Pipeline

```text
interface class
    -> compile / cache lookup
    -> candidate inspection
    -> per-member validation
    -> error aggregation
    -> success or InterfaceValidationError
```

## Compilation

Compilation should occur before candidate validation and should normalize interface metadata into an immutable `CompiledInterface`.

Compilation responsibilities include:

- resolving type hints;
- collecting inherited members;
- identifying member kinds;
- normalizing method signatures;
- identifying async functions;
- preserving source annotations for diagnostics;
- preparing assignability metadata;
- detecting unsupported or contradictory declarations.

## Candidate inspection

Inspection should be conservative about side effects.

Prefer static inspection such as `inspect.getattr_static` when identifying member presence and descriptor kind. Avoid invoking properties or arbitrary descriptors just to discover whether a member exists.

Runtime-value validation, if enabled, may require ordinary attribute access and therefore must be documented as potentially invoking descriptors.

## Method validation

For each required method:

1. Verify the member exists.
2. Verify that it is callable in the expected binding context.
3. Normalize the implementation signature.
4. Compare call-shape compatibility.
5. Validate parameter type assignability.
6. Validate return type assignability.
7. Validate sync/async compatibility.

Do not stop after the first parameter mismatch. Collect independent member errors where practical.

## Attribute validation

For declared attributes, the engine should distinguish declaration validation from current-value validation.

Initial behavior should support current instance value validation where a safe runtime type check is meaningful, but must avoid claiming that a matching current value proves a writable attribute has the correct long-term contract.

## Property validation

A property should be inspected as a descriptor and its getter return annotation validated.

Writable property support should eventually validate setter compatibility separately.

## Dynamic members

Objects may provide members through `__getattr__` or `__getattribute__`.

Recommended policy:

- permissive mode may allow a dynamic member to satisfy existence when it can be accessed;
- strict mode should require inspectable contract information when signature/type compatibility cannot otherwise be proven;
- diagnostics should explain that the member is dynamic rather than silently treating it as an ordinary declaration.

## Decorators and wrapped functions

Use `inspect.unwrap` where appropriate so well-behaved decorators using `functools.wraps` preserve the underlying contract.

If a wrapper intentionally changes the public signature, the exposed signature should win.

## Async validation

The initial implementation should distinguish ordinary `def` and `async def` directly.

Do not automatically equate:

```python
async def f() -> T
```

with:

```python
def f() -> Awaitable[T]
```

until a deliberate semantic rule is designed and tested.

Future support should separately address:

- generators;
- async generators;
- context managers;
- async context managers.

## Configuration

A small initial config surface is preferable.

Conceptual options:

```python
InterfaceConfig(
    strict=False,
    validate_values=True,
)
```

Avoid adding many policy switches before real use cases demonstrate the need.

## Adapters

`InterfaceAdapter` should compile once and validate many candidates:

```python
adapter = InterfaceAdapter(Storage)

adapter.validate_python(local_storage)
adapter.validate_python(s3_storage)
```

This should be the preferred form for high-throughput or framework usage.

## Failure policy

Validation should fail closed when a requested strict guarantee cannot be proven.

Unsupported typing constructs must not silently become equality checks or unconditional acceptance.

Permissive behavior should be explicit and narrowly defined.
