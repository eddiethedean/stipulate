from __future__ import annotations

import gc
import threading
import types
import weakref
from typing import cast

import pytest
from tests_support import dynamic_contract, requirement

from stipulate import ContractError


def test_local_self_referential_declaration_and_ir_are_collectable() -> None:
    req = requirement("class Requirement(Protocol):\n def f(self, x:int=0) -> int: ...")
    method = cast(types.FunctionType, getattr(req, "f"))
    method.__defaults__ = (req,)
    checked = dynamic_contract(req)
    req_ref = weakref.ref(cast(type[object], req))
    ir_ref = weakref.ref(getattr(checked, "_ir"))
    del req, method, checked
    gc.collect()
    assert req_ref() is None and ir_ref() is None


def test_concurrent_refresh_and_checks_keep_independent_results() -> None:
    req = requirement("class Requirement(Protocol):\n def f(self) -> int: ...")

    class Candidate:
        def f(self) -> int:
            return 1

    retained = dynamic_contract(req)
    barrier = threading.Barrier(4)
    failures: list[BaseException] = []
    snapshots: list[object] = []

    def run() -> None:
        try:
            barrier.wait(timeout=5)
            for _ in range(20):
                refreshed = dynamic_contract(req, refresh=True)
                snapshots.append(refreshed)
                first = retained.check(Candidate())
                second = refreshed.check(Candidate())
                assert first.compatible and second.compatible
                assert first.evidence is not second.evidence
        except BaseException as error:
            failures.append(error)

    workers = [threading.Thread(target=run) for _ in range(4)]
    for worker in workers:
        worker.start()
    for worker in workers:
        worker.join(timeout=10)
        assert not worker.is_alive()
    assert not failures and len(snapshots) == 80


def test_rejection_records_follow_exact_enforcement_policy() -> None:
    req = requirement("class Requirement(Protocol):\n def f(self, x:int) -> str: ...")

    class Candidate:
        def f(self, x: object) -> str:
            return ""

    Candidate.f.__annotations__ = {"return": "UnavailableName"}
    checked = dynamic_contract(req)
    for strict, expected in (
        (True, {"annotation_missing", "annotation_unresolved"}),
        (False, {"annotation_unresolved"}),
    ):
        with pytest.raises(ContractError) as caught:
            checked.validate(Candidate(), strict=strict)
        assert {row["type"] for row in caught.value.errors()} == expected
        exported = caught.value.errors()
        exported[0]["loc"].append("mutation")
        assert "mutation" not in caught.value.errors()[0]["loc"]
