"""Remaining invariants from Sol re-review 02; production stays unchanged."""

from __future__ import annotations

import inspect
from collections.abc import Callable
from pathlib import Path
from typing import Tuple, cast

import pytest
from test_sol_review_blockers import return_result
from tests_support import dynamic_contract, requirement
from typing_extensions import TypeForm

from stipulate import CompatibilityStatus, Contract
from stipulate._compile import ContractIR, MethodIR
from tools import benchmark


def test_sol_001_static_lookup_does_not_execute_class_equality() -> None:
    calls: list[str] = []

    class Meta(type):
        def __eq__(cls, other: object) -> bool:
            calls.append("equality")
            return False

        __hash__ = type.__hash__

    class Candidate(metaclass=Meta):
        def __getattribute__(self, name: str) -> object:
            calls.append("lookup")
            raise AssertionError("Custom lookup must not run")

        def f(self) -> int:
            raise AssertionError("Candidate operations must not run")

    # Custom lookup is unsupported, and can be rejected statically without
    # consulting the owner's equality hook or executing instance lookup.
    declaration = requirement("class Requirement(Protocol):\n def f(self) -> int: ...")
    result = dynamic_contract(declaration).check(Candidate())
    assert result.status is CompatibilityStatus.UNKNOWN
    assert not result.accepted(strict=False)
    assert calls == [], "Static class-owner classification must use identity"


class TupleSubclass(tuple[object, ...]):
    pass


@pytest.mark.parametrize("provided", [Tuple, TupleSubclass])
def test_sol_005_bare_tuple_destination_alias_preserves_nominal_proofs(provided: object) -> None:
    assert return_result(tuple, provided).compatible
    result = return_result(Tuple, provided)
    assert result.compatible and result.complete


def test_sol_006_custom_assignment_dispatch_also_intercepts_property_writes() -> None:
    calls: list[str] = []

    class Candidate:
        @property
        def value(self) -> int:
            calls.append("getter")
            return 1

        @value.setter
        def value(self, value: int) -> None:
            calls.append("setter")

        def __setattr__(self, name: str, value: object) -> None:
            calls.append("assignment")
            raise AttributeError("All assignment is intercepted")

    readonly = requirement("class Requirement(Protocol):\n @property\n def value(self) -> int: ...")
    writable = requirement("class Requirement(Protocol):\n value: int")
    candidate = Candidate()
    assert dynamic_contract(readonly).check(candidate).compatible
    result = dynamic_contract(writable).check(candidate)
    assert calls == []
    assert not result.compatible
    assert not result.accepted(strict=False)


def test_sol_008_wide_benchmark_has_independent_keyword_presence_choices(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    latest: list[Contract[object]] = []
    independent_choices: list[bool] = []

    def recording_contract(declaration: TypeForm[object], **options: object) -> Contract[object]:
        compiled = dynamic_contract(declaration, **options)
        latest.append(compiled)
        return compiled

    def measure(
        workload: str, operation: Callable[[], object], iterations: int
    ) -> dict[str, object]:
        if "wide" in workload:
            ir = cast(ContractIR, getattr(latest[-1], "_ir"))
            independent_choices.append(
                any(
                    sum(
                        parameter.kind is inspect.Parameter.KEYWORD_ONLY
                        and parameter.default is not inspect.Parameter.empty
                        for parameter in member.signature.parameters.values()
                    )
                    > 1
                    for member in ir.members
                    if isinstance(member, MethodIR)
                )
            )
        operation()
        return {"workload": workload, "iterations": iterations, "seconds": 0.0}

    def digest(root: Path) -> str:
        return "a" * 64

    monkeypatch.setattr(benchmark, "Contract", recording_contract)
    monkeypatch.setattr(benchmark, "measure", measure)
    monkeypatch.setattr(benchmark, "source_digest", digest)
    monkeypatch.setattr(
        benchmark.stipulate, "__file__", "/verification/site-packages/stipulate/__init__.py"
    )
    distribution = tmp_path / "verification-only.whl"
    distribution.write_bytes(b"Synthetic verification only; never measured release evidence")
    benchmark.run(tmp_path, distribution, 1)
    assert any(independent_choices), (
        "The wide keyword-only benchmark must exercise multiple independent optional keywords; "
        "one mandatory keyword has only one legal presence subset"
    )
