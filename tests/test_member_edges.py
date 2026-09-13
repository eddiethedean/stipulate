from __future__ import annotations

import inspect
from typing import Protocol

import pytest
from tests_support import dynamic_contract, requirement

from stipulate import CompatibilityStatus, Contract, ContractDefinitionError


def test_sync_wrapper_does_not_inherit_wrapped_coroutine_kind() -> None:
    class Required(Protocol):
        async def f(self) -> int: ...

    async def wrapped(self: object) -> int:
        return 1

    class Candidate:
        def f(self) -> object:
            raise AssertionError("not called")

    setattr(Candidate.f, "__wrapped__", wrapped)
    result = Contract(Required).check(Candidate())
    assert result.complete and result.errors()[0]["type"] == "async_mismatch"


def test_malformed_setter_call_shape_is_not_permissible_type_uncertainty() -> None:
    req = requirement("class Requirement(Protocol):\n value:int")

    class Candidate:
        @property
        def value(self) -> int:
            return 1

        @value.setter
        def value(self, *, assigned: int) -> None:
            raise AssertionError("not called")

    result = dynamic_contract(req).check(Candidate())
    assert not result.accepted(strict=False)
    assert result.unknowns()[0]["type"] == "signature_unavailable"
    with pytest.raises(ContractDefinitionError):
        dynamic_contract(
            requirement(
                "class Requirement(Protocol):\n @property\n def value(self) -> int: ...\n"
                " @value.setter\n def value(self, *, assigned:int) -> None: ..."
            )
        )


def test_unknown_getter_preserves_known_missing_write_capability() -> None:
    req = requirement("class Requirement(Protocol):\n value:int")

    class Candidate:
        @property
        def value(self) -> int:
            return 1

    getter = vars(Candidate)["value"].fget
    setattr(getter, "__signature__", "invalid")
    result = dynamic_contract(req).check(Candidate())
    assert result.status is CompatibilityStatus.INCOMPATIBLE and not result.complete
    assert result.errors()[0]["loc"] == ["value", "write"]
    assert result.unknowns()[0]["loc"] == ["value", "read"]


def test_malformed_explicit_signature_stops_recovery() -> None:
    req = requirement("class Requirement(Protocol):\n def f(self) -> int: ...")

    class Candidate:
        def f(self) -> int:
            return 1

    signature = inspect.Signature(
        [
            inspect.Parameter("x", inspect.Parameter.KEYWORD_ONLY),
            inspect.Parameter("receiver", inspect.Parameter.POSITIONAL_ONLY),
        ],
        return_annotation=int,
        __validate_parameters__=False,
    )
    setattr(Candidate.f, "__signature__", signature)
    assert dynamic_contract(req).check(Candidate()).unknowns()[0]["type"] == "signature_unavailable"


@pytest.mark.parametrize("candidate", [None, 1, "text", b"x", [], {}, ()])
def test_primitives_report_conclusive_missing_capabilities(candidate: object) -> None:
    req = requirement("class Requirement(Protocol):\n def required_operation(self) -> int: ...")
    result = dynamic_contract(req).check(candidate)
    assert result.status is CompatibilityStatus.INCOMPATIBLE
    assert result.errors()[0]["type"] == "missing_member"


def test_plain_noncallable_storage_is_a_known_method_kind_mismatch() -> None:
    req = requirement("class Requirement(Protocol):\n def f(self) -> int: ...")

    class Candidate:
        f = 1

    result = dynamic_contract(req).check(Candidate())
    assert result.status is CompatibilityStatus.INCOMPATIBLE
    assert result.errors()[0]["type"] == "member_kind"
