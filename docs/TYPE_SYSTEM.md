# Type System and Assignability

## Authority and scope

Follow the Python typing specification for supported annotation relations. Stipulate-specific runtime policies, including strict evidence and execution-kind requirements, must be labeled as policies. Checker differences are recorded, not silently treated as language semantics.

The exact 0.1 subset is in ROADMAP.md. Unsupported required annotations are definition errors. Unsupported candidate annotations yield unknown evidence and fail both strict and permissive enforcement.

## Callable relations

A provided callable must accept every call permitted by the required callable. Parameters are contravariant; returns are covariant. Include positional-only, positional-or-keyword, keyword-only, names usable as keywords, defaults, variadics, binding, and extra required parameters.

Normalize legal calls and prove their containment deterministically. Random/sample calls are test oracles for bounded cases, not the production compatibility algorithm. Preserve parameter correlations when variadics or unions are present.

For a required parameter Dog and return Animal, an implementation accepting Animal and returning Dog is compatible. Reversing these relations is not.

## Gradual and missing types

Missing candidate annotations yield `annotation_missing` when a required type obligation cannot be established. Any is an explicit gradual type, not evidence of semantic equality and not interchangeable with object.

Use `gradual_type` if establishing a relation depends on Any materialization. Such evidence is UNKNOWN and can be tolerated only explicitly with `strict=False`. Relations established without using that wildcard can remain conclusive: ordinary supported values assignable to object do not become unknown solely because unrelated metadata is gradual.

An explicit required Any requests gradual typing, not a guarantee of accepting every Python object. Preserve it as Any and report UNKNOWN when the required relation relies on its wildcard behavior, including in strict mode. Do not reinterpret it as object. It does not excuse unknown member presence or call shape. In evolution analysis, a relation involving a gradual contract cannot establish a universal guarantee merely because Python permits a gradual assignment. The relation context must enforce this distinction.

Unsupported forms are never accepted through identity/equality fallback. Validate that a form is supported before applying any reflexive fast path.

Required callable parameters and returns must have annotations in 0.1, except the bound receiver. Missing required annotations are definition errors; explicit Any remains available to express deliberate gradual typing.

## Initial nominal and special forms

Support None/NoneType, ordinary nominal classes, unions, Literal, and Annotated underlying types with metadata preserved for diagnostics. Nominal subclass relations must account for Python typing's documented numeric promotions rather than assuming issubclass alone is sufficient (for example int is accepted where float is expected).

Literal identity includes both value and its type: Literal[True] is not interchangeable with Literal[1] merely because True == 1. Normalize unions without losing nominal identities or making branch order affect outcomes.

Annotated metadata has no validation meaning in 0.1. Constraints such as positivity are not enforced or used for narrowing. Examples must not treat Pydantic PositiveInt, which uses Annotated metadata, as a distinct nominal subtype of int.

## Initial collection forms

Use explicit, tested rules for list[T], set[T], dict[K, V], fixed and homogeneous variadic tuple types, and the documented read abstractions Sequence[T], Iterable[T], and Mapping[K, V]. Mutable containers are invariant; tuple/Sequence/Iterable elements are covariant; Mapping keys are invariant and values covariant under their declared typing relationships.

Cross-origin relations require a supported origin inheritance/substitution map, for example list[int] to Sequence[object]. Matching origins alone is insufficient. Bare generics and erased type arguments use gradual evidence where obligations depend on the missing arguments.

This finite origin table does not imply arbitrary user-defined generic specialization. Unknown origins and unsupported recursive forms remain explicit.

## Members and mutability

A readable member provides a type covariantly. A writable member must also accept the required write type contravariantly. Equal getter and setter types therefore often require invariance. A read-only property cannot satisfy a writable attribute contract.

Do not infer declaration assignability from a matching current value. The core does not recursively validate collection contents, invoke property getters, or check future values returned by methods.

## Resolution and aliases

Compile ordinary resolvable string annotations and legacy aliases under the selected annotation policy. Preserve source expressions for errors. Unresolvable required names fail definition compilation; candidate-only failures are unknown evidence.

Local-scope namespaces cannot always be recovered. Provide explicit namespace mappings as an advanced constructor option and test ownership/cache behavior. TYPE_CHECKING-only imports are not automatically imported to make evaluation succeed.

PEP 695 aliases, recursive aliases, nested Protocol types, user-defined generics, Self, overloads, ParamSpec, Concatenate, TypeVarTuple, Unpack, and typed kwargs remain separately gated. A newer interpreter does not automatically enable those semantics.

## Sources

- [Callable assignability](https://typing.python.org/en/latest/spec/callables.html)
- [Protocol semantics](https://typing.python.org/en/latest/spec/protocol.html)
- [Gradual type relations](https://typing.python.org/en/latest/spec/concepts.html)

The conformance corpus records relevant specification sections, checker versions, and intentional runtime-policy deviations.
