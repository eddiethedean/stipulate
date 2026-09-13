from __future__ import annotations

import gc
import inspect
import json
import threading
import types
import weakref
from typing import Callable, Protocol, cast

import pytest
from typing_extensions import TypeForm

from stipulate import CompatibilityStatus as S
from stipulate import Contract, ContractDefinitionError, ContractError
from stipulate._compile import ContractIR


def snapshot(value: object) -> ContractIR:
    return cast(ContractIR, getattr(value, "_ir"))


def declaration(source: str, extra: dict[str, object] | None = None) -> object:
    namespace: dict[str, object] = {"Protocol": Protocol, "__name__": __name__, **(extra or {})}
    exec(compile(source, "<fixture>", "exec", dont_inherit=True), namespace)
    return namespace["Requirement"]


def contract(value: object, **options: object) -> Contract[object]:
    # Runtime negative fixtures are deliberately broader than the public TypeForm.
    if options:
        factory = cast(Callable[..., Contract[object]], Contract)
        return factory(value, **options)
    return Contract(cast(TypeForm[object], value))


def test_invalid_declarations_and_required_nested_types() -> None:
    for value in (
        int,
        1,
        list[int],
        declaration("class Base(Protocol): pass\nclass Requirement(Base): pass"),
    ):
        with pytest.raises(ContractDefinitionError) as caught:
            contract(value)
        assert caught.value.code == "invalid_contract"
        assert caught.value.phase == "declaration"
    with pytest.raises(ContractDefinitionError) as caught:
        contract(
            declaration(
                "class Requirement(Protocol):\n def f(self, x:list[list[int, str]]) -> int: ..."
            )
        )
    assert caught.value.phase == "types"


def test_inherited_conflicts_overrides_and_diamonds() -> None:
    prefix = (
        "class A(Protocol):\n def f(self, x:int) -> object: ...\n"
        "class B(Protocol):\n def f(self, x:str) -> object: ...\n"
    )
    with pytest.raises(ContractDefinitionError, match="inherited") as caught:
        contract(declaration(prefix + "class Requirement(A, B, Protocol): pass"))
    assert caught.value.code == "conflicting_member"
    value = declaration(
        prefix + "class Requirement(A, B, Protocol):\n def f(this, x:object) -> str: ..."
    )
    assert len(snapshot(contract(value)).members) == 1
    diamond = declaration(
        "class A(Protocol):\n def f(self) -> int: ...\nclass B(A, Protocol): pass\n"
        "class C(A, Protocol): pass\nclass Requirement(B,C,Protocol): pass"
    )
    assert len(snapshot(contract(diamond)).members) == 1


def test_signature_layers_receiver_cycles_and_independent_kind() -> None:
    req = declaration("class Requirement(Protocol):\n async def f(this, x:int) -> int: ...")

    class Candidate:
        def f(self, x: object) -> int:
            return 1

    setattr(
        Candidate.f,
        "__signature__",
        inspect.Signature(
            [
                inspect.Parameter("receiver", inspect.Parameter.POSITIONAL_ONLY),
                inspect.Parameter("x", inspect.Parameter.POSITIONAL_OR_KEYWORD, annotation=object),
            ],
            return_annotation=int,
        ),
    )
    result = contract(req).check(Candidate())
    assert result.complete and result.errors()[0]["type"] == "async_mismatch"
    setattr(Candidate.f, "__signature__", "malformed")
    result = contract(req).check(Candidate())
    assert result.status is S.INCOMPATIBLE and not result.complete
    assert "signature_unavailable" in {d["type"] for d in result.unknowns()}
    delattr(Candidate.f, "__signature__")
    setattr(Candidate.f, "__wrapped__", Candidate.f)
    assert "signature_unavailable" in {
        d["type"] for d in contract(req).check(Candidate()).unknowns()
    }


def test_independent_resolution_and_namespace_isolation() -> None:
    req = declaration("class Requirement(Protocol):\n def f(self, x:int) -> 'Payload': ...")
    with pytest.raises(ContractDefinitionError) as caught:
        contract(req)
    assert caught.value.code == "annotation_unresolved"
    good = contract(req, localns={"Payload": int})

    class Candidate:
        def f(self, x: str) -> int:
            return 1

    Candidate.f.__annotations__ = {"x": str, "return": "Payload"}
    result = good.check(Candidate())
    assert result.status is S.INCOMPATIBLE and not result.complete
    assert result.errors()[0]["loc"] == ["f", "x"]
    assert result.unknowns()[0]["type"] == "annotation_unresolved"
    assert not result.accepted(strict=False)


def test_raw_never_evaluates_expressions_or_deferred_factories() -> None:
    calls: list[str] = []

    def expression() -> type[int]:
        calls.append("expression")
        return int

    req = declaration(
        "class Requirement(Protocol):\n def f(self) -> expression(): ...",
        {"expression": expression},
    )
    calls.clear()
    # On <=3.13 the eager expression is already materialized; raw may use it.
    try:
        contract(req, annotations="raw")
    except ContractDefinitionError as caught:
        assert caught.code == "annotation_unresolved"
    assert calls == []
    req = declaration(
        "class Requirement(Protocol):\n def f(self) -> 'expression()': ...",
        {"expression": expression},
    )
    with pytest.raises(ContractDefinitionError):
        contract(req, annotations="raw")
    assert calls == []


def test_storage_mutability_hooks_slots_and_no_value_inference() -> None:
    req = declaration("class Requirement(Protocol):\n value:int")

    class Wider:
        value: object = 1

    result = contract(req).check(Wider())
    assert result.status is S.INCOMPATIBLE and result.complete
    assert result.errors()[0]["loc"] == ["value", "read"]

    class Unannotated:
        value = 1

    assert contract(req).check(Unannotated()).accepted(strict=False)

    class Slots:
        __slots__ = ("value",)
        value: int

        def __init__(self) -> None:
            self.value = 1

    assert contract(req).check(Slots()).unknowns()[0]["type"] == "descriptor_unverifiable"
    calls: list[str] = []

    class Hook:
        def __getattribute__(self, name: str) -> object:
            calls.append(name)
            raise AssertionError("must not execute")

    assert contract(req).check(Hook()).status is S.UNKNOWN
    assert calls == []


def test_properties_support_storage_and_never_call_getter_setter() -> None:
    req = declaration("class Requirement(Protocol):\n @property\n def value(self) -> int: ...")

    class Storage:
        value: int = 1

    assert contract(req).check(Storage()).compatible
    writable = declaration("class Requirement(Protocol):\n value:int")

    class Property:
        @property
        def value(self) -> int:
            raise AssertionError("getter called")

        @value.setter
        def value(self, assigned: object) -> None:
            raise AssertionError("setter called")

    assert contract(writable).check(Property()).compatible


def test_snapshot_refresh_failure_candidate_mutation_and_collection() -> None:
    req = declaration("class Requirement(Protocol):\n def f(self) -> int: ...")
    old = contract(req)
    method = cast(types.FunctionType, getattr(req, "f"))
    method.__annotations__ = {"return": str}
    new = contract(req, refresh=True)
    assert snapshot(old) is not snapshot(new)
    method.__annotations__ = {}
    with pytest.raises(ContractDefinitionError):
        contract(req, refresh=True)
    assert snapshot(contract(req)) is snapshot(new)
    reference, ir_ref = weakref.ref(cast(type[object], req)), weakref.ref(snapshot(old))
    del req, old, new, method
    gc.collect()
    assert reference() is None and ir_ref() is None


def test_concurrent_first_use_shares_live_snapshot_and_evidence_is_independent() -> None:
    req = declaration("class Requirement(Protocol):\n def f(self) -> int: ...")
    barrier = threading.Barrier(8)
    results: list[Contract[object]] = []
    errors: list[BaseException] = []

    def run() -> None:
        try:
            barrier.wait(timeout=5)
            results.append(contract(req))
        except BaseException as error:
            errors.append(error)

    threads = [threading.Thread(target=run) for _ in range(8)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=10)
        assert not thread.is_alive()
    assert not errors and len(results) == 8
    assert all(snapshot(c) is snapshot(results[0]) for c in results)


def test_safe_render_json_and_exception_readonly_fields() -> None:
    req = declaration("class Requirement(Protocol):\n def f(self) -> int: ...")
    setattr(req, "__name__", "unsafe\x1b[31m\n" + "x" * 100)
    checked = contract(req)
    result = checked.check(object())
    text = str(result)
    assert "\x1b" not in text and all(len(line) <= 60 for line in text.splitlines())
    json.dumps(result.errors() + result.unknowns(), allow_nan=False)
    with pytest.raises(ContractError) as caught:
        checked.validate(object())
    for field in ("result", "strict"):
        with pytest.raises(AttributeError):
            setattr(caught.value, field, None)


def test_annotation_baseexceptions_and_internal_bugs_propagate() -> None:
    def stop() -> None:
        raise KeyboardInterrupt

    req = declaration("class Requirement(Protocol):\n def f(self) -> 'stop()': ...", {"stop": stop})
    with pytest.raises(KeyboardInterrupt):
        contract(req)
