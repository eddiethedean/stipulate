# Static Typing Strategy

## Permanent baseline

All first-party implementation code and promoted valid examples must pass Pyright strict with zero errors. Runtime introspection is normalized behind small typed boundaries. No blanket Any, disabled diagnostics, or file-wide ignores are accepted to make the public API appear typed.

Mypy is a required public interoperability target. Record its supported versions and any feature settings separately from Pyright. Both checkers must preserve the interface type returned by the advertised validation API.

## Typed Contract constructor

The planned public signature uses a type-form parameter, not a constructible-class parameter:

```python
from typing import Generic, TypeVar
from typing_extensions import TypeForm

T = TypeVar("T")

class Contract(Generic[T]):
    def __init__(self, declaration: TypeForm[T], ...) -> None: ...
    def validate(self, candidate: object, *, strict: bool = True) -> T: ...
```

This is a signature sketch, not executable implementation code. TypeForm expresses the input/output type relationship without implying that the supplied Protocol can be instantiated. Runtime compilation still restricts inputs to the supported Protocol subset.

Users write `storage_contract = Contract(Storage)`; checkers should infer `Contract[Storage]`, and `.validate(candidate)` should return Storage. The constructor must not degrade to an unrelated object parameter with caller-selected T: that would allow `Contract[int](Storage)` to claim an unrelated return type.

## Verified design evidence

The fixtures in ../design_probes/ exercise the proposed signature, structural composition, exact return inference, incompatible explicit type arguments, and negative implementations. They are static declaration probes, not a working validator.

On the recorded local environment, Pyright 1.1.411 and mypy 1.19.1 pass the positive TypeForm probe. Mypy 1.19.1 requires `--enable-incomplete-feature=TypeForm`; this is a checker feature flag, not a plugin. The recorded typing_extensions version is 4.15.0.

These are tested versions, not claimed minimum versions. Release CI must pin and prove its checker matrix. If the flag remains necessary at release, put the exact setting in setup documentation. Do not silently replace TypeForm with Any to support older checkers. Evaluate later checker versions before freezing 0.1 requirements.

## Rejected fallback

```python
def validate(interface: type[T], candidate: object) -> T: ...
```

Passing a Protocol class to this generic signature is accepted in the tested Pyright configuration but rejected by the tested mypy with `type-abstract`. It is not a checker-neutral fallback. The declaration probe preserves this disagreement as expected evidence.

## Structural composition

Use an explicit special Protocol base:

```python
class Storage(Readable, Writable, Protocol):
    pass
```

Omitting Protocol creates an ordinary class for static analysis. Runtime metaclass changes cannot repair that interpretation. Positive and negative fixtures must cover single inheritance, multiple inheritance, overrides, and structural implementations with no nominal relationship.

## Experimental Interface bridge

The desired `class Foo(Interface):` plus `Foo.validate()` is separately gated. A typing-facing import re-export of Protocol can support the initial declaration but does not automatically describe custom metaclass methods. An assignment alias is not equivalent across checkers. A standard class containing helper methods risks contaminating protocol requirements.

Promotion requires all of:

- valid and invalid structural assignments under both checkers;
- precise class-side return inference without Any leakage;
- runtime member discovery excludes every framework helper;
- explicit structural extension/composition works statically and at runtime;
- normal module, installed wheel, and installed sdist usage works;
- no consumer ignores, generated per-interface stubs, or required checker plugins;
- each advertised Python version passes runtime and checker fixtures.

Keep the bridge experimental if any requirement remains unresolved. Contract(Protocol) remains the released method-based path; unresolved shorthand does not block 0.1.

## Packaging

Ship py.typed and complete public type information. Private typing implementation classes must not appear in public annotations. If stubs are used, check their agreement with the runtime and test an installed distribution outside the source tree. A clean in-repository checker run alone is insufficient.

TypeForm requires typing_extensions on supported older interpreters; dependency minimums must be derived from the tested release matrix. Static acceptance of broader type forms does not imply runtime support for non-Protocol declarations.

## Suppressions

Narrow suppressions require a documented genuine checker limitation and a precisely typed surrounding API. Intentionally invalid fixtures assert expected diagnostic codes instead of suppressing them. A fixture that merely reveals the desired type while also producing errors is not a passing example.

## Sources

- [TypeForm specification](https://typing.python.org/en/latest/spec/type-forms.html)
- [Protocol composition and class-object rules](https://typing.python.org/en/latest/spec/protocol.html)
