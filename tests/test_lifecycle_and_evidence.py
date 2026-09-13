from __future__ import annotations

from typing import Callable, Protocol, cast

import pytest

from stipulate import CompatibilityStatus, Contract
from stipulate._compile import ContractIR


def snapshot(value: object) -> ContractIR:
    return cast(ContractIR, getattr(value, "_ir"))


class Marker(Protocol):
    def ping(self) -> None: ...


class Impl:
    def ping(self) -> None: ...


def test_live_contract_reuses_immutable_requirement_snapshot() -> None:
    first = Contract(Marker)
    second = Contract(Marker)
    assert snapshot(first) is snapshot(second)
    assert first.check(Impl()).status is CompatibilityStatus.COMPATIBLE


def test_custom_namespaces_bypass_shared_cache() -> None:
    first = Contract(Marker, globalns={})
    second = Contract(Marker, globalns={})
    assert snapshot(first) is not snapshot(second)


def test_exported_diagnostics_are_independent_and_evidence_is_frozen() -> None:
    class Missing(Protocol):
        def run(self, value: int) -> str: ...

    result = Contract(Missing).check(object())
    exported = result.errors()
    exported[0]["loc"].append("mutated")
    assert result.errors()[0]["loc"] == ["run"]
    with pytest.raises(TypeError):
        cast(dict[str, object], result.evidence[0].ctx)["new"] = "value"


def test_strict_argument_is_rejected_when_not_bool() -> None:
    with pytest.raises(TypeError):
        cast(Callable[..., object], Contract(Marker).validate)(Impl(), strict=1)
