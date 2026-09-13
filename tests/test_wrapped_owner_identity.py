from __future__ import annotations

import gc
import weakref
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
@pytest.mark.parametrize("class_cell", [False, True])
def test_decorated_method_and_property_locals_require_recorded_owner(
    accessor: bool, class_cell: bool
) -> None:
    declaration = " @property\n" if accessor else ""
    selected = "Original.f.fget" if accessor else "Original.f"
    body = "__class__.Local()" if class_cell else "'text'"
    namespace: dict[str, object] = {}
    exec(
        "from functools import wraps\ncalls=[]\n"
        "def decorate(function):\n @wraps(function)\n def wrapper(*args,**kwargs):\n"
        "  calls.append('wrapper')\n  return function(*args,**kwargs)\n return wrapper\n"
        "class Original:\n Local=str\n" + declaration + " @decorate\n def f(self)->'Local':\n"
        "  calls.append('operation')\n  return " + body + "\n"
        "class Candidate:\n @wraps(" + selected + ")\n def f(self): ...\n",
        namespace,
    )
    req = requirement("class Requirement(Protocol):\n def f(self)->int: ...")
    candidate = cast(type[object], namespace["Candidate"])()
    result = dynamic_contract(req).check(candidate)
    if class_cell:
        assert result.status.value == "incompatible" and result.complete
        assert result.errors()[0]["actual"] == "str"
    else:
        assert result.status.value == "unknown" and not result.complete
        assert result.unknowns()[0]["type"] == "annotation_unresolved"
    assert not result.accepted(strict=True) and not result.accepted(strict=False)
    assert namespace["calls"] == []


@pytest.mark.parametrize("replacement", ["selected", "decorate(selected)"])
@pytest.mark.parametrize("class_cell", [False, True])
def test_original_owner_provenance_survives_global_replacement_or_is_unavailable(
    replacement: str, class_cell: bool
) -> None:
    namespace: dict[str, object] = {}
    body = "__class__.Local()" if class_cell else "'text'"
    exec(
        "from functools import wraps\ncalls=[]\n"
        "def decorate(function):\n @wraps(function)\n def wrapper(*args,**kwargs):\n"
        "  calls.append('wrapper')\n  return function(*args,**kwargs)\n return wrapper\n"
        "class Original:\n Local=str\n def f(self)->'Local':\n"
        "  calls.append('operation')\n  return " + body + "\nselected=Original.f\n",
        namespace,
    )
    original = weakref.ref(cast(type[object], namespace["Original"]))
    exec(
        "class Original:\n Local=int\n f=" + replacement + "\n"
        "class Candidate:\n f=decorate(selected)\n",
        namespace,
    )
    gc.collect()
    # There is no retained global alias to help recover the old class. Its
    # compiler-created cell is the only owner reference when one exists.
    assert (original() is not None) is class_cell
    req = requirement("class Requirement(Protocol):\n def f(self)->int: ...")
    contract = dynamic_contract(req)
    candidate = cast(type[object], namespace["Candidate"])()
    result = contract.check(candidate)
    if class_cell:
        assert result.status.value == "incompatible" and result.complete
        assert result.errors()[0]["actual"] == "str"
    else:
        assert result.status.value == "unknown" and not result.complete
        assert result.unknowns()[0]["type"] == "annotation_unresolved"
    for strict in (True, False):
        assert not result.accepted(strict=strict)
        with pytest.raises(ContractError):
            contract.validate(candidate, strict=strict)
    assert namespace["calls"] == []


@pytest.mark.parametrize("annotations", ["trusted", "raw"])
def test_wrapped_materialized_types_do_not_require_owner_recovery(annotations: str) -> None:
    namespace: dict[str, object] = {}
    exec(
        "from functools import wraps\ncalls=[]\n"
        "class Original:\n def f(self): calls.append('operation')\n"
        "Original.f.__annotations__={'return':int}\n"
        "class Candidate:\n @wraps(Original.f)\n def f(self): calls.append('wrapper')\n",
        namespace,
    )
    req = requirement("class Requirement(Protocol):\n def f(self)->int: ...")
    # Materialize requirement metadata as well, including on deferred runtimes.
    getattr(req, "f").__annotations__ = {"return": int}
    contract = dynamic_contract(req, annotations=annotations)
    candidate = cast(type[object], namespace["Candidate"])()
    result = contract.check(candidate)
    assert result.compatible and result.complete
    assert contract.validate(candidate) is candidate
    assert namespace["calls"] == []


def test_selected_free_function_uses_its_globals_despite_copied_class_qualname() -> None:
    namespace: dict[str, object] = {}
    exec(
        "from functools import wraps\nfrom inspect import Parameter, Signature\n"
        "Local=str\ncalls=[]\nclass Original:\n Local=int\n def f(self): ...\n"
        "@wraps(Original.f)\ndef selected(self): calls.append('selected')\n"
        "selected.__signature__=Signature([Parameter('self', Parameter.POSITIONAL_ONLY)],"
        " return_annotation='Local')\n"
        "class Candidate:\n @wraps(selected)\n def f(self): calls.append('candidate')\n",
        namespace,
    )
    req = requirement("class Requirement(Protocol):\n def f(self)->int: ...")
    candidate = cast(type[object], namespace["Candidate"])()
    result = dynamic_contract(req).check(candidate)
    assert result.status.value == "incompatible" and result.complete
    assert result.errors()[0]["actual"] == "str"
    assert namespace["calls"] == []
