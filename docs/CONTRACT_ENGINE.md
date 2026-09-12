# Contract Engine

## Purpose

Stipulate is designed as a contract engine for Python structural interfaces. Runtime validation is the first application of the engine, not the architectural primitive.

The semantic center is a directional relation:

```text
provided contract <= required contract
```

meaning that the provided side can safely be used where the required side is expected.

## Five core operations

### Compile

```python
contract = compile_contract(Storage)
```

Convert a Python `Interface` or supported `Protocol` into immutable canonical semantic metadata.

### Inspect

```python
result = inspect_contract(Storage, candidate)
```

Compile the requirement, inspect the candidate, and return a non-throwing `CompatibilityResult` containing evidence.

### Enforce

```python
storage = validate(Storage, candidate)
```

Interpret a compatibility result according to validation policy. Successful validation returns the original object. Incompatibility, and unknown evidence under strict policy, raises `InterfaceValidationError`.

### Compare

```python
report = compare_interfaces(StorageV1, StorageV2)
```

Compare two explicit contracts directionally. Evolution analysis must distinguish compatibility for existing implementers from compatibility for existing consumers rather than flattening all changes into one textual diff.

### Serialize

```python
schema = contract.schema()
fingerprint = contract.fingerprint()
```

Produce a canonical versioned representation suitable for schemas, snapshots, hashing, CI, documentation, and future interoperability.

## Contract IR

The compiled representation should be semantic and deliberately smaller than a Python source/API AST.

Conceptually:

```text
Contract
  identity/display metadata
  members
    MethodContract
      callable shape
      async/generator semantics
      normalized TypeExpr parameters
      normalized TypeExpr return
    AttributeContract
      read type
      write type if applicable
    PropertyContract
      read/write capabilities
  generic bindings/parameters
  schema version
```

The IR must not contain candidate-specific validation state.

## CompatibilityResult

All compatibility analysis should converge on a common immutable result model.

Conceptually:

```python
CompatibilityResult(
    status=CompatibilityStatus.COMPATIBLE,
    assurance=Assurance.COMPLETE,
    evidence=(...),
)
```

The result should support at least three semantic outcomes:

- `COMPATIBLE`: no incompatible evidence exists and policy-required facts are established;
- `INCOMPATIBLE`: at least one contract requirement is disproven;
- `UNKNOWN`: compatibility cannot be proven or disproven from available metadata.

Do not collapse unknown evidence into success internally. Permissive validation may choose to tolerate unknown evidence as policy, but the underlying result must preserve it.

## Evidence

Evidence is the explanation layer of the engine, not merely an error-message implementation detail.

An evidence record should contain enough structured information for human rendering, validation errors, CI, and tooling:

```python
Evidence(
    loc=("get", "key"),
    status=EvidenceStatus.PROVEN,
    code="parameter_assignable",
    expected=str,
    actual=str,
    source="annotation",
)
```

Unknown evidence should explain why proof is unavailable:

```python
Evidence(
    loc=("get", "return"),
    status=EvidenceStatus.UNKNOWN,
    code="implementation_annotation_missing",
    expected=bytes,
)
```

Incompatible evidence should explain the violated semantic relation, not merely print two unequal annotations.

## Assurance

Assurance summarizes how completely Stipulate could establish a result from available runtime metadata.

Initial conceptual levels:

- `COMPLETE`: all relevant requirements were established from supported evidence;
- `PARTIAL`: some requirements are unknown but none are disproven;
- `NONE`: insufficient evidence exists for meaningful proof.

Exact public enum design remains subject to OTP acceptance tests. Assurance must not be statistical confidence and must not imply observed runtime behavior that Stipulate did not execute.

## Object validation and contract comparison share semantics

The validator and evolution engine must not implement separate compatibility rules.

For object validation, candidate introspection creates a provided-contract view and compares it to the required interface contract.

For interface evolution, both sides are explicit contracts.

This shared engine is a core differentiator and correctness requirement.

## Directional evolution

Given old and new interface contracts, Stipulate should eventually report at least two perspectives.

### Implementer compatibility

Will implementations satisfying the old interface necessarily satisfy the new interface?

### Consumer compatibility

Can consumers written against the old interface safely interact with values described by the new contract?

These directions may disagree because callable parameters are contravariant and return values are covariant.

A report should preserve that distinction:

```python
report.implementer_compatible
report.consumer_compatible
```

## Canonical serialization

The canonical schema is Stipulate's semantic interchange representation. It should be deterministic and versioned.

It powers:

- `interface_schema()`;
- snapshots;
- fingerprints;
- compatibility baselines;
- documentation/tooling;
- possible future native-core boundaries.

Canonicalization rules must specify member ordering, type normalization, aliases, unions, defaults, qualified names, generic parameters, and schema-version behavior before fingerprints become public compatibility guarantees.

## Fingerprints

A fingerprint should identify a canonical semantic contract, not source formatting.

Conceptually:

```text
stipulate-contract-v1:sha256:<digest>
```

Fingerprints are useful for identity, caching, manifests, and baseline checks. They do not themselves establish compatibility: two different fingerprints can still represent mutually compatible contracts.

## Snapshots and CI

A future CLI can serialize explicit contracts as repository baselines:

```text
stipulate snapshot
stipulate check
```

`check` should perform semantic compatibility analysis rather than source/text diffing.

The CLI must remain a consumer of the same contract engine used by the Python API.

## Capability analysis

Structural interfaces naturally represent capabilities. Future tooling may inspect an object against multiple contracts:

```python
inspect_capabilities(obj, [Readable, Writable, Transactional])
```

This should remain contract-engine functionality rather than turning Stipulate into a plugin or dependency-injection framework.

## Rust-ready boundary

The initial implementation should remain Python unless benchmarks justify a native core. However, the IR and compatibility engine should avoid depending directly on live `inspect.Parameter`, descriptor, and arbitrary `typing` objects after compilation.

A future architecture could be:

```text
Python introspection and annotation resolution
                ↓
       canonical Contract IR
                ↓
        compatibility core
```

If a Rust core is later justified, PyO3/maturin can consume normalized IR without moving Python introspection into Rust.

## Architectural rule

New features should be expressible as composition over the five primitives whenever practical:

```text
validate = compile + inspect + enforce
explain = inspect + render
compare_interfaces = compile + compare
snapshot = compile + serialize
fingerprint = compile + canonical serialize + hash
CI check = snapshot/baseline + compare + policy
```

If a feature requires an independent semantic compatibility implementation, that is a warning that the core abstraction is leaking.