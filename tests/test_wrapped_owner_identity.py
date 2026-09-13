from __future__ import annotations

from typing import cast

import pytest
from tests_support import dynamic_contract, requirement

from stipulate import ContractError


def test_final_001_replacement_class_cannot_supply_wrapped_annotation_locals() -> None:
    namespace: dict[str, object] = {}
    exec(
        "from functools import wraps\ncalls=[]\n"
        "class Original:\n Local=str\n def f(self)->'Local':\n"
        "  calls.append('operation')\n  return 'text'\n"
        "original_owner=Original\n"
        "class Candidate:\n @wraps(Original.f)\n def f(self):\n"
        "  return self.f.__wrapped__(self)\n"
        "class Original:\n Local=int\n def f(self)->'Local': return 1\n",
        namespace,
    )
    req = requirement("class Requirement(Protocol):\n def f(self)->int: ...")
    contract = dynamic_contract(req)
    candidate = cast(type[object], namespace["Candidate"])()
    result = contract.check(candidate)
    assert result.status.value == "unknown" and not result.complete
    assert result.unknowns()[0]["type"] == "annotation_unresolved"
    for strict in (True, False):
        assert not result.accepted(strict=strict)
        with pytest.raises(ContractError):
            contract.validate(candidate, strict=strict)
    assert namespace["calls"] == []


@pytest.mark.parametrize("accessor", [False, True])
def test_authenticated_owner_retains_decorated_method_and_property_locals(accessor: bool) -> None:
    declaration = " @property\n" if accessor else ""
    selected = "Original.f.fget" if accessor else "Original.f"
    namespace: dict[str, object] = {}
    exec(
        "from functools import wraps\ncalls=[]\n"
        "def decorate(function):\n @wraps(function)\n def wrapper(*args,**kwargs):\n"
        "  calls.append('wrapper')\n  return function(*args,**kwargs)\n return wrapper\n"
        "class Original:\n Local=str\n" + declaration + " @decorate\n def f(self)->'Local':\n"
        "  calls.append('operation')\n  return 'text'\n"
        "class Candidate:\n @wraps(" + selected + ")\n def f(self): ...\n",
        namespace,
    )
    req = requirement("class Requirement(Protocol):\n def f(self)->int: ...")
    candidate = cast(type[object], namespace["Candidate"])()
    result = dynamic_contract(req).check(candidate)
    assert result.status.value == "incompatible" and result.complete
    assert result.errors()[0]["actual"] == "str"
    assert namespace["calls"] == []
