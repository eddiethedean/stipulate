# Validation Engine

## Pipeline

`Contract(ProtocolType)` compiles a requirement snapshot. `contract.check(candidate)` statically inspects the candidate and returns a policy-independent result. `contract.validate(candidate, strict=True)` checks, enforces the acceptance table, and returns the original candidate on success.

Compilation errors use `ContractDefinitionError`; rejection under enforcement uses `ContractError`. See CONTRACT_ENGINE.md for exact outcomes.

## Annotation policies

Default `annotations="trusted"` resolves annotations with controlled namespaces and the standard runtime facilities appropriate to the supported Python version. Request include_extras where appropriate to preserve Annotated metadata. Annotation expressions and deferred evaluation functions can execute Python code. Loading a plugin already executes code; Stipulate is not a sandbox or a guarantee that introspection has no effects.

`annotations="raw"` does not request evaluation of strings, forward references, or deferred annotation functions. It uses only metadata that can be obtained without that evaluation. Unresolved required types cause definition errors; unresolved candidate types become `annotation_unresolved` unknowns. Do not claim this mode makes arbitrary object introspection secure or undoes evaluation already performed by Python.

No attempt should automatically import TYPE_CHECKING-only names. Advanced `globalns` and `localns` mappings apply to the requirement declaration only. Candidate annotations use their own defining module and owner context; never resolve them against the requirement namespace merely because names match. Unavailable candidate-local names remain unknown. The constructor mappings are copied for stable key/value bindings (referenced objects are not deep-frozen). Custom namespaces bypass the shared global compilation cache in 0.1. Document that annotation resolution can fail for unavailable function-local names.

Supplied requirement globalns entries overlay each selected declaration's defining globals; localns entries overlay its declaring owner locals, with ordinary local lookup precedence. Inherited declarations retain their defining context. Resolve independent annotations separately where possible so an unresolved return cannot hide a known parameter mismatch. Supplying either mapping, even an empty one, bypasses shared caching.

On CPython 3.14, raw mode must avoid deferred __annotations__ getters and annotation functions even when requested in STRING/FORWARDREF format. Passing eval_str=False to inspect.signature is insufficient: deferred annotations may still be evaluated. Recover input shapes without requesting annotation evaluation. If no non-evaluating path can obtain a required annotation or member set, fail construction with annotation_unresolved; candidate-only metadata remains non-permissible annotation_unresolved uncertainty. Materialized dictionaries/explicit Signature metadata may be used only when obtainable without invoking an annotation factory. This is a deliberately narrower raw subset, not a sandbox. [Python's annotationlib documentation](https://docs.python.org/3.14/library/annotationlib.html#security-implications-of-introspecting-annotations) describes these evaluation effects. The [phase 0.1 contract](PHASE_0_1_IMPLEMENTATION_CONTRACT.md#annotations-and-trust-boundaries) defines the testable boundary.

## Static member inspection

Use static lookup to determine declaration presence, member kind, and supported storage. Do not call candidate methods, property getters, custom descriptor accessors, or dynamic __getattr__ hooks to gather evidence. Do not claim static inspection establishes how a custom __getattribute__ implementation will behave.

Plain Python methods with standard binding and supported attributes/properties form the initial supported subset. Unknown custom lookup/binding behavior produces `dynamic_member_unverifiable` or `descriptor_unverifiable` rather than a fabricated missing member or compatible declaration. Conservatively handle custom attribute dispatch that can intercept required members.

Extra candidate members are allowed and do not enter the required-member analysis. Class-object candidates are outside 0.1 instance validation: report an explicit unsupported-candidate outcome rather than inferring instances, invoking constructors, or applying incorrect binding.

## Methods

1. Establish member presence and supported binding.
2. Recover the externally exposed signature using the precedence below.
3. Check containment of all legal required calls.
4. Compare parameter and return declarations directionally.
5. Check supported execution kind.
6. Aggregate independent evidence in deterministic order.

If presence fails, report that root cause and record dependent obligations as unassessed rather than emitting misleading parameter errors.

## Signature precedence

Use an explicit __signature__ when well-formed; otherwise follow a well-formed __wrapped__ chain as inspect.signature does; otherwise inspect the visible Python callable. Bound-method normalization must happen exactly once. Preserve the metadata source in evidence and detect wrapper cycles and malformed overrides.

The exposed signature is a trusted declaration; wraps does not prove a wrapper preserves behavior. Unavailable, malformed, or unsupported signatures yield non-permissible unknown evidence. Do not execute representative calls to recover a signature.

## Attributes and properties

Support statically declared plain instance/class storage and standard property descriptors for the documented cases. For an instance-required attribute, a class annotation alone does not establish initialized storage. Verify supported storage presence without reading through user descriptors. Uninitialized slots require explicit handling; if presence cannot be established without executing a descriptor, report uncertainty.

Use declared read/write types. A property getter's return annotation establishes its declared read type; a setter parameter establishes its declared write type. A current value is not a declaration and is not checked for recursive value conformance in 0.1.

Properties are never invoked to see whether they return the annotated value. Dynamic attributes, custom descriptors, cached_property, and generated framework storage remain unsupported unless a later explicit handler passes its gates.

In 0.1, ordinary instance dictionaries and plain class storage establish supported presence; annotations alone do not. Standard slots yield descriptor_unverifiable uncertainty when initialization cannot be established without executing their descriptor. With ordinary __getattribute__, a __getattr__ hook affects statically absent members rather than automatically invalidating statically present supported ones. See the [storage and dynamic-uncertainty contract](PHASE_0_1_IMPLEMENTATION_CONTRACT.md#storage-properties-and-dynamic-uncertainty) for presence, read/write, mutability, and hook boundaries.

## Async policy

0.1 distinguishes ordinary Python def and coroutine async def. An async declaration requires a coroutine implementation declaration. A synchronous function annotated as returning Awaitable is not automatically accepted. Conversely, an unexpected coroutine declaration fails a required ordinary def policy.

This is an intentional execution-kind policy in addition to typing assignability; it is stricter than some callable substitutions allowed by static typing. Normalize coroutine result annotations consistently and do not wrap them twice.

Async generators, generators, callable objects, and unusual decorator-induced execution kinds remain unsupported until their own normalization rules pass tests. Class and static methods are outside the 0.1 subset.

## Failure handling

Known candidate mismatches become incompatible findings. Expected inspection limitations become unknown findings with reason and provenance. Requirement failures raise definition errors. Catch only documented inspection/resolution failures at their boundary; never turn arbitrary internal bugs, KeyboardInterrupt, or SystemExit into compatibility evidence.

## Value validation

Current-value validation is not enabled in core 0.1. A later explicit operation may execute attribute access and validate values, with a separately named policy and result. Optional Pydantic integration must not coerce and discard a replacement value while returning an unchanged, invalid candidate as “validated.”
