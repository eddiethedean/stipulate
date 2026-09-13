from __future__ import annotations

import inspect
import sys
import types
from functools import wraps
from typing import Protocol, cast

import pytest
from tests_support import dynamic_contract, requirement

from stipulate import Contract


class WrappedOwner:
    Local = str

    def f(self) -> "Local":
        return "text"


class WrappedCandidate:
    Local = int

    @wraps(WrappedOwner.f)
    def f(self) -> object:
        return WrappedOwner.f(cast(WrappedOwner, self))


def test_inherited_methods_use_their_own_module_and_owner(monkeypatch: pytest.MonkeyPatch) -> None:
    required_module = types.ModuleType("stipulate_requirement_fixture")
    candidate_module = types.ModuleType("stipulate_candidate_fixture")
    monkeypatch.setitem(sys.modules, required_module.__name__, required_module)
    monkeypatch.setitem(sys.modules, candidate_module.__name__, candidate_module)
    exec(
        "from typing import Protocol\nAlias=int\nclass Base(Protocol):\n"
        " def f(self, x:'Alias') -> 'Alias': ...\nclass Requirement(Base,Protocol): pass",
        required_module.__dict__,
    )
    exec(
        "Alias=str\nclass Base:\n Local=Alias\n def f(self, x:'Local') -> 'Alias': return x\n"
        "class Candidate(Base): pass",
        candidate_module.__dict__,
    )
    checked = dynamic_contract(getattr(required_module, "Requirement"))
    candidate = getattr(candidate_module, "Candidate")()
    result = checked.check(candidate)
    assert result.complete and len(result.errors()) == 2
    assert result.errors()[0]["expected"] == "int" and result.errors()[0]["actual"] == "str"
    assert (
        dynamic_contract(getattr(required_module, "Requirement"), globalns={"Alias": str})
        .check(candidate)
        .compatible
    )


def test_explicit_signature_and_wrapped_layers_do_not_merge_annotations() -> None:
    req = requirement("class Requirement(Protocol):\n def f(self, x:int) -> int: ...")

    class Candidate:
        def f(self, x: str) -> str:
            raise AssertionError("not executed")

    def wrapped(self: object, x: object) -> int:
        raise AssertionError("not executed")

    setattr(Candidate.f, "__wrapped__", wrapped)
    assert dynamic_contract(req).check(Candidate()).compatible

    # An intermediate override wins, even when the final function disagrees.
    signature = inspect.Signature(
        [
            inspect.Parameter("receiver", inspect.Parameter.POSITIONAL_ONLY),
            inspect.Parameter("x", inspect.Parameter.POSITIONAL_OR_KEYWORD, annotation=object),
        ],
        return_annotation=int,
    )
    setattr(wrapped, "__signature__", signature)
    setattr(wrapped, "__wrapped__", Candidate.f)
    assert dynamic_contract(req).check(Candidate()).compatible
    setattr(Candidate.f, "__signature__", signature)
    assert dynamic_contract(req).check(Candidate()).compatible


def test_wrapped_annotations_use_the_selected_function_owner() -> None:
    req = requirement("class Requirement(Protocol):\n def f(self) -> int: ...")

    result = dynamic_contract(req).check(WrappedCandidate())

    assert result.status.value == "incompatible"
    assert result.complete
    assert result.errors()[0]["expected"] == "int"
    assert result.errors()[0]["actual"] == "str"


def test_raw_explicit_signature_avoids_all_annotation_factories() -> None:
    calls: list[str] = []

    def factory(*args: object) -> object:
        calls.append("factory")
        raise AssertionError("factory executed")

    class Requirement(Protocol):
        def f(self, x: int) -> int: ...

    class Candidate:
        def f(self, x: int) -> int:
            return x

    signature = inspect.Signature(
        [
            inspect.Parameter("receiver", inspect.Parameter.POSITIONAL_ONLY),
            inspect.Parameter("x", inspect.Parameter.POSITIONAL_OR_KEYWORD, annotation=int),
        ],
        return_annotation=int,
    )
    for method in (Requirement.f, Candidate.f):
        setattr(method, "__signature__", signature)
        setattr(method, "__annotate__", factory)
    assert Contract(Requirement, annotations="raw").check(Candidate()).compatible
    assert calls == []


def test_annotation_exception_details_do_not_leak_into_diagnostics(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def expression() -> type[int]:
        raise RuntimeError("secret-value")

    class Requirement(Protocol):
        def f(self) -> int: ...

    class Candidate:
        def f(self) -> int:
            return 1

    Candidate.f.__annotations__ = {"return": "expression()"}
    monkeypatch.setitem(Candidate.f.__globals__, "expression", expression)
    result = Contract(Requirement).check(Candidate())
    assert result.unknowns()[0]["type"] == "annotation_unresolved"
    assert "secret-value" not in str(result) and not result.accepted(strict=False)
