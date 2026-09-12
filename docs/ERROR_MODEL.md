# Error Model

## Objective

Stipulate errors should be as useful and composable as Pydantic validation errors.

A validation failure should report all meaningful independent contract mismatches in one exception.

```python
try:
    validate(Repository, candidate)
except InterfaceValidationError as exc:
    print(exc)
    errors = exc.errors()
```

## Exception hierarchy

Initial public hierarchy:

```text
StipulateError
└── InterfaceValidationError
```

Compilation/configuration failures may later use separate exceptions such as:

```text
InterfaceDefinitionError
UnsupportedTypeError
```

Avoid a large exception hierarchy before real use cases require it.

## Structured error shape

`InterfaceValidationError.errors()` should return stable dictionaries or typed records with fields similar to:

```python
{
    "loc": ("save", "value"),
    "type": "parameter_type",
    "msg": "Implementation parameter type is too narrow",
    "expected": "str",
    "actual": "bytes",
    "ctx": {},
}
```

## Location model

Locations should be tuples so nested diagnostics remain machine-readable.

Examples:

```text
("get",)
("get", "id")
("get", "return")
("config",)
("property_name", "getter", "return")
```

## Error codes

Initial stable codes should include:

- `missing_member`
- `member_kind`
- `not_callable`
- `signature`
- `parameter_missing`
- `parameter_kind`
- `parameter_required`
- `parameter_type`
- `return_type`
- `async_mismatch`
- `attribute_type`
- `property_type`
- `annotation_missing`
- `annotation_unresolved`
- `unsupported_type`
- `dynamic_member_unverifiable`

Error code names become part of the ecosystem once users build tooling around them, so additions are easier than renames.

## Rendering

Human-readable rendering should be concise and deterministic.

Example:

```text
3 validation errors for Repository

get.id
  Implementation parameter type is too narrow
  Expected acceptance: int
  Found: str
  [type=parameter_type]

get.return
  Return type is not assignable to interface return type
  Expected: User | None
  Found: int
  [type=return_type]

save
  Async method required but synchronous method found
  [type=async_mismatch]
```

## Expected and actual values

Error objects should preserve original type objects internally when useful, while serialization/rendering should use stable readable representations.

Avoid relying directly on implementation-specific `repr()` output for public serialization.

## Aggregation

The engine should continue validation after independent failures where safe.

One broken member should not hide unrelated errors in other members.

Within a single signature, report enough detail to explain the problem without flooding the user with redundant derivative errors.

## Unsupported constructs

Unsupported typing constructs are not ordinary type mismatches. They should be distinguishable so users know Stipulate could not prove compatibility rather than believing the implementation is necessarily invalid.

Strict mode should fail closed with `unsupported_type` where a guarantee cannot be made.

## Programmatic stability

Before 1.0, error details may evolve, but `loc`, `type`, and `msg` should be treated as the minimum long-term public shape.

The 1.0 release should document compatibility guarantees for error codes and serialized error records.
