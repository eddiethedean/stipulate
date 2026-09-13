"""Remaining FINAL-001 ownership invariant from Sol production re-review."""

from __future__ import annotations

from typing import cast

import pytest
from tests_support import dynamic_contract, requirement

from stipulate import ContractError


def test_final_001_wrapping_a_retained_function_does_not_prove_its_defining_owner() -> None:
    namespace: dict[str, object] = {}
    exec(
        "from functools import wraps\ncalls=[]\n"
        "class Original:\n Local=str\n def f(self)->'Local':\n"
        "  calls.append('operation')\n  return 'text'\n"
        "original_owner=Original\n"
        "class Candidate:\n @wraps(original_owner.f)\n def f(self):\n"
        "  return original_owner.f(self)\n"
        "class Original:\n Local=int\n @wraps(original_owner.f)\n def f(self):\n"
        "  return original_owner.f(self)\n",
        namespace,
    )
    # All declarations precede compilation. The selected function, its original
    # owner and its truthful annotations remain unchanged; no concurrent mutation
    # or candidate execution is involved in the check.
    req = requirement("class Requirement(Protocol):\n def f(self)->int: ...")
    contract = dynamic_contract(req)
    candidate = cast(type[object], namespace["Candidate"])()
    result = contract.check(candidate)
    assert namespace["calls"] == []
    for strict in (True, False):
        assert not result.accepted(strict=strict), (
            "A class exposing a wrapped function is not necessarily its defining owner"
        )
        with pytest.raises(ContractError):
            contract.validate(candidate, strict=strict)
    assert namespace["calls"] == []
