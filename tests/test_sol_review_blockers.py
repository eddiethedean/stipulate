"""Release-blocking verification from Sol review 01; production is unchanged."""

from __future__ import annotations

import inspect
import unicodedata
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol, Tuple, cast

import pytest
from tests_support import dynamic_contract, requirement
from typing_extensions import TypeForm

from stipulate import CompatibilityResult, CompatibilityStatus, Contract, ContractDefinitionError
from stipulate._compile import ContractIR, MethodIR
from tools import benchmark


def exposed_return(method: object, returned: object) -> None:
    # Actual types in explicit metadata work under raw policy on every target.
    setattr(
        method,
        "__signature__",
        inspect.Signature(
            [inspect.Parameter("receiver", inspect.Parameter.POSITIONAL_ONLY)],
            return_annotation=returned,
        ),
    )


def return_result(required: object, provided: object) -> CompatibilityResult:
    declaration = requirement("class Requirement(Protocol):\n def f(self) -> int: ...")
    exposed_return(getattr(declaration, "f"), required)

    class Candidate:
        def f(self) -> object:
            raise AssertionError("Candidate operations must not run")

    exposed_return(Candidate.f, provided)
    return dynamic_contract(declaration, annotations="raw").check(Candidate())


def test_sol_001_cache_distinguishes_equal_protocol_class_objects() -> None:
    namespace: dict[str, object] = {"Protocol": Protocol}
    exec(
        "class Meta(type(Protocol)):\n"
        " def __eq__(cls, other): return type(other) is Meta\n"
        " def __hash__(cls): return 17\n"
        "class First(Protocol, metaclass=Meta):\n def first(self) -> int: ...\n"
        "class Second(Protocol, metaclass=Meta):\n def second(self) -> int: ...\n"
        "class Candidate:\n def first(self) -> int: return 1\n",
        namespace,
    )
    candidate = cast(type[object], namespace["Candidate"])()
    first = dynamic_contract(namespace["First"])
    second = dynamic_contract(namespace["Second"])
    assert first.check(candidate).compatible
    fresh = dynamic_contract(namespace["Second"], refresh=True)
    assert fresh.check(candidate).status is CompatibilityStatus.INCOMPATIBLE
    assert second.check(candidate).status is CompatibilityStatus.INCOMPATIBLE


def test_sol_001_nominal_proof_preserves_identity_without_metaclass_equality() -> None:
    calls: list[str] = []

    class Meta(type):
        def __eq__(cls, other: object) -> bool:
            calls.append("equality")
            return True

        __hash__ = type.__hash__

    class Unrelated(metaclass=Meta):
        pass

    result = return_result(float, Unrelated)
    assert calls == [], "A nominal proof must not execute overloaded class equality"
    assert result.status is CompatibilityStatus.INCOMPATIBLE


def test_sol_002_private_marker_does_not_make_a_normal_class_a_protocol() -> None:
    class Normal:
        _is_protocol = True

        def f(self) -> int:
            return 1

    with pytest.raises(ContractDefinitionError) as caught:
        dynamic_contract(Normal)
    assert caught.value.code == "invalid_contract"
    assert caught.value.phase == "declaration"


def test_sol_003_numeric_promotions_include_nominal_subclasses() -> None:
    class SmallInt(int):
        pass

    class SmallFloat(float):
        pass

    for required, provided in ((float, SmallInt), (complex, SmallFloat)):
        result = return_result(required, provided)
        assert result.compatible and result.complete


def test_sol_004_foreign_instance_dictionary_descriptor_is_an_inspection_limit() -> None:
    class Other:
        pass

    candidate_type = type("Candidate", (), {"__dict__": Other.__dict__["__dict__"]})
    declaration = requirement("class Requirement(Protocol):\n def f(self) -> int: ...")
    result = dynamic_contract(declaration).check(candidate_type())
    assert result.status is CompatibilityStatus.UNKNOWN
    assert not result.accepted(strict=False)
    empty = requirement("class Requirement(Protocol): pass")
    assert dynamic_contract(empty).check(candidate_type()).compatible


@pytest.mark.parametrize("provided", [tuple[int], tuple[int, ...]])
def test_sol_005_bare_typing_tuple_is_not_a_fixed_empty_tuple(provided: object) -> None:
    assert return_result(tuple, provided).compatible
    result = return_result(Tuple, provided)
    assert result.compatible and result.complete


def test_sol_006_frozen_storage_does_not_prove_writable_capability() -> None:
    writable = requirement("class Requirement(Protocol):\n value: int")
    readonly = requirement("class Requirement(Protocol):\n @property\n def value(self) -> int: ...")

    @dataclass(frozen=True)
    class Frozen:
        value: int = 1

    candidate = Frozen()
    assert dynamic_contract(readonly).check(candidate).compatible
    result = dynamic_contract(writable).check(candidate)
    assert not result.compatible
    assert not result.accepted(strict=False)


def test_sol_007_exported_type_labels_escape_control_characters() -> None:
    class Payload:
        pass

    Payload.__name__ = "Bad\x1b[31m\nLabel"
    result = return_result(int, Payload)
    assert result.status is CompatibilityStatus.INCOMPATIBLE
    actual = result.errors()[0]["actual"]
    assert actual is not None and "Bad" in actual and "Label" in actual
    assert not any(unicodedata.category(c).startswith("C") for c in actual)


def test_sol_009_async_generator_property_requirement_fails_eagerly() -> None:
    declaration = requirement(
        "class Requirement(Protocol):\n @property\n async def value(self) -> int:\n  yield 1"
    )
    with pytest.raises(ContractDefinitionError) as caught:
        dynamic_contract(declaration)
    assert caught.value.code == "invalid_contract"
    assert caught.value.phase == "members"


def test_sol_008_wide_benchmark_exercises_keyword_only_partition(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Probe actual benchmark declarations; guard/digest/timing stubs are test-only.
    latest: list[Contract[object]] = []
    wide_keyword_only: list[bool] = []

    def recording_contract(declaration: TypeForm[object], **options: object) -> Contract[object]:
        compiled = dynamic_contract(declaration, **options)
        latest.append(compiled)
        return compiled

    def measure(
        workload: str, operation: Callable[[], object], iterations: int
    ) -> dict[str, object]:
        if "wide" in workload:
            ir = cast(ContractIR, getattr(latest[-1], "_ir"))
            wide_keyword_only.append(
                any(
                    p.kind is inspect.Parameter.KEYWORD_ONLY
                    for member in ir.members
                    if isinstance(member, MethodIR)
                    for p in member.signature.parameters.values()
                )
            )
        operation()
        return {"workload": workload, "iterations": iterations, "seconds": 0.0}

    monkeypatch.setattr(benchmark, "Contract", recording_contract)
    monkeypatch.setattr(benchmark, "measure", measure)

    def digest(root: Path) -> str:
        return "a" * 64

    monkeypatch.setattr(benchmark, "source_digest", digest)
    monkeypatch.setattr(
        benchmark.stipulate, "__file__", "/verification/site-packages/stipulate/__init__.py"
    )
    distribution = tmp_path / "verification-only.whl"
    distribution.write_bytes(b"Synthetic verification input; never release evidence")
    benchmark.run(tmp_path, distribution, 1)
    assert any(wide_keyword_only), "The approved plan requires a wide keyword-only benchmark"
