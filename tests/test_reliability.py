from __future__ import annotations

import gc
import importlib
import threading
import weakref
from typing import Any, Protocol

import pytest
from tests_support import dynamic_contract, requirement

from stipulate import CompatibilityStatus, Contract, ContractDefinitionError


def test_any_union_keeps_known_failure_and_independent_uncertainty() -> None:
    req = requirement("class Requirement(Protocol):\n def f(self) -> str: ...")

    class Candidate:
        def f(self) -> str:
            return ""

    Candidate.f.__annotations__ = {"return": Any | int}
    result = dynamic_contract(req).check(Candidate())
    assert result.status is CompatibilityStatus.INCOMPATIBLE and not result.complete
    assert result.errors()[0]["type"] == "return_type"
    assert result.unknowns()[0]["type"] == "gradual_type"


def test_metaclass_lookup_hooks_are_never_executed() -> None:
    calls: list[str] = []

    class Meta(type):
        def __getattribute__(cls, name: str) -> object:
            calls.append(name)
            return type.__getattribute__(cls, name)

    class Candidate(metaclass=Meta):
        value: int = 1

    calls.clear()
    req = requirement("class Requirement(Protocol):\n value:int")
    result = dynamic_contract(req).check(Candidate())
    assert result.status is CompatibilityStatus.UNKNOWN and calls == []


def test_custom_getattr_present_and_absent_members() -> None:
    req = requirement("class Requirement(Protocol):\n value:int")
    calls: list[str] = []

    class Candidate:
        value: int = 1

        def __getattr__(self, name: str) -> object:
            calls.append(name)
            return 1

    assert dynamic_contract(req).check(Candidate()).compatible
    delattr(Candidate, "value")
    result = dynamic_contract(req).check(Candidate())
    assert result.unknowns()[0]["type"] == "dynamic_member_unverifiable"
    assert calls == []


def test_unwritable_class_storage_and_readonly_property() -> None:
    req = requirement("class Requirement(Protocol):\n value:int")

    class ClassStorage:
        __slots__ = ()
        value: int = 1

    assert dynamic_contract(req).check(ClassStorage()).errors()[0]["type"] == "member_kind"

    class ReadOnly:
        @property
        def value(self) -> int:
            raise AssertionError("getter")

    result = dynamic_contract(req).check(ReadOnly())
    assert result.complete and result.errors()[0]["loc"] == ["value", "write"]


def test_unsupported_bindings_generators_and_callable_values() -> None:
    req = requirement("class Requirement(Protocol):\n def f(self) -> int: ...")

    class Static:
        @staticmethod
        def f() -> int:
            raise AssertionError("called")

    class Generator:
        def f(self) -> object:
            yield 1

    for candidate in (Static(), Generator(), type("Callable", (), {"f": len})()):
        result = dynamic_contract(req).check(candidate)
        assert not result.accepted(strict=False) and result.status is CompatibilityStatus.UNKNOWN
    with pytest.raises(ContractDefinitionError):
        dynamic_contract(
            requirement("class Requirement(Protocol):\n def f(self) -> int:\n  yield 1")
        )


def test_candidate_mutation_is_observed_without_refresh() -> None:
    req = requirement("class Requirement(Protocol):\n def f(self) -> int: ...")

    class Candidate:
        def f(self) -> int:
            return 1

    checked = dynamic_contract(req)
    candidate = Candidate()
    assert checked.check(candidate).compatible
    Candidate.f.__annotations__ = {"return": str}
    assert checked.check(candidate).status is CompatibilityStatus.INCOMPATIBLE
    ref = weakref.ref(candidate)
    del candidate
    gc.collect()
    assert ref() is None


def test_render_never_calls_value_default_or_annotated_metadata_repr() -> None:
    calls: list[str] = []

    class Explosive:
        def __repr__(self) -> str:
            calls.append("repr")
            raise AssertionError("repr executed")

    metadata = Explosive()
    req = requirement(
        "from typing import Annotated\nclass Requirement(Protocol):\n"
        " def f(self, x:Annotated[int, metadata]=metadata) -> int: ...",
        {"metadata": metadata},
    )

    class Candidate:
        def f(self, x: object = metadata) -> str:
            return ""

        def __repr__(self) -> str:
            raise AssertionError("candidate repr")

    checked = dynamic_contract(req)
    result = checked.check(Candidate())
    assert "return_type" in str(result) and repr(result).startswith("CompatibilityResult(")
    assert repr(checked) == "Contract[Requirement]" and calls == []


def test_reentrant_annotation_compilation_is_not_under_the_cache_lock() -> None:
    marker = requirement("class Requirement(Protocol): pass")
    completed: list[bool] = []

    def evaluate() -> type[int]:
        def work() -> None:
            dynamic_contract(marker)
            completed.append(True)

        worker = threading.Thread(target=work)
        worker.start()
        worker.join(timeout=5)
        assert not worker.is_alive()
        return int

    req = requirement(
        "class Requirement(Protocol):\n def f(self) -> 'evaluate()': ...", {"evaluate": evaluate}
    )
    dynamic_contract(req)
    assert completed == [True]


def test_definition_exception_readonly_and_failed_frames_collectable() -> None:
    class Payload:
        pass

    ref = weakref.ref(Payload)
    req = requirement(
        "class Requirement(Protocol):\n def f(self) -> 'missing(Payload)': ...",
        {"Payload": Payload},
    )
    with pytest.raises(ContractDefinitionError) as caught:
        dynamic_contract(req)
    for name in ("code", "loc", "phase", "msg", "hint"):
        with pytest.raises(AttributeError):
            setattr(caught.value, name, "mutated")
    del caught, req, Payload
    gc.collect()
    assert ref() is None


def test_explicit_namespace_bindings_are_copied() -> None:
    req = requirement("class Requirement(Protocol):\n def f(self) -> 'Payload': ...")
    bindings: dict[str, object] = {"Payload": int}
    checked = dynamic_contract(req, localns=bindings)
    bindings["Payload"] = str

    class Candidate:
        def f(self) -> int:
            return 1

    assert checked.check(Candidate()).compatible


def test_missing_obligations_have_root_references_and_exact_json_fields() -> None:
    req = requirement("class Requirement(Protocol):\n def f(self, x:int, *, y:str) -> str: ...")
    result = dynamic_contract(req).check(None)
    assert not result.complete and result.status is CompatibilityStatus.INCOMPATIBLE
    unknowns = result.unknowns()
    assert len(unknowns) == 5
    for row in unknowns:
        assert row["ctx"]["root_loc"] == ["f"]
        assert set(row) == {
            "loc",
            "type",
            "status",
            "msg",
            "expected",
            "actual",
            "source",
            "hint",
            "ctx",
        }
    unknowns[0]["ctx"]["root_loc"] = ["changed"]
    assert result.unknowns()[0]["ctx"]["root_loc"] == ["f"]


def test_unexpected_engine_exception_propagates(monkeypatch: pytest.MonkeyPatch) -> None:
    module = importlib.import_module("stipulate._compatibility")

    class Req(Protocol):
        def f(self) -> int: ...

    class Candidate:
        def f(self) -> int:
            return 1

    def fault(*args: object, **kwargs: object) -> None:
        raise RuntimeError("engine bug")

    monkeypatch.setattr(module, "check_signature", fault)
    with pytest.raises(RuntimeError, match="engine bug"):
        Contract(Req).check(Candidate())
