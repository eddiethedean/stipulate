from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Callable, Protocol, cast

import pytest

from stipulate import Contract, ContractDefinitionError


class Storage(Protocol):
    def read(self, key: str, *, fresh: bool = False) -> bytes: ...
    def write(self, key: str, value: bytes) -> None: ...


class MemoryStorage:
    def __init__(self) -> None:
        self.values: dict[str, bytes] = {}

    def read(self, key: str, *, fresh: bool = False) -> bytes:
        return self.values.get(key, b"")

    def write(self, key: str, value: bytes) -> None:
        self.values[key] = value


def test_installed_quickstart_real_operations_and_identity() -> None:
    plugin = MemoryStorage()
    storage = Contract(Storage).validate(plugin)
    assert storage is plugin
    storage.write("greeting", b"hello")
    assert storage.read("greeting") == b"hello"


@pytest.mark.parametrize("filename", ["README.md", "docs/QUICKSTART.md"])
def test_actual_documentation_python_blocks(filename: str) -> None:
    root = Path(__file__).parents[1]
    text = (root / filename).read_text().split("## Interface shorthand", 1)[0]
    namespace: dict[str, object] = {}
    for block in re.findall(r"```python\n(.*?)```", text, flags=re.S):
        exec(compile(block, filename, "exec", dont_inherit=True), namespace)


@pytest.mark.parametrize(
    "scenario",
    [
        "compatible",
        "parameter",
        "call-shape",
        "missing-type",
        "unavailable",
        "mixed",
        "empty",
        "definition",
    ],
)
def test_actual_report_scenarios(scenario: str) -> None:
    catalogue = json.loads(
        (Path(__file__).parents[1] / "docs/examples/report_scenarios.json").read_text()
    )
    row = next(item for item in catalogue["scenarios"] if item["id"] == scenario)
    if scenario == "definition":

        class DefinitionStorage(Protocol):
            def read(self) -> int: ...

        DefinitionStorage.read.__annotations__ = {"return": "Payload"}
        setattr(DefinitionStorage, "__name__", "Storage")
        with pytest.raises(ContractDefinitionError) as caught:
            Contract(DefinitionStorage)
        assert str(caught.value).startswith(row["headline"])
        return
    candidate = MemoryStorage()
    # Isolate function dictionaries so fixtures never mutate another scenario.
    import types

    original = MemoryStorage.read
    method = types.FunctionType(
        original.__code__, original.__globals__, original.__name__, original.__defaults__
    )
    method.__kwdefaults__ = original.__kwdefaults__
    method.__annotations__ = dict(original.__annotations__)
    impl = type("Candidate", (MemoryStorage,), {"read": method})
    candidate = impl()
    contract = Contract(Storage)
    if scenario == "parameter":
        method.__annotations__["key"] = bytes
    elif scenario == "call-shape":
        import inspect

        setattr(
            method,
            "__signature__",
            inspect.Signature(
                [
                    inspect.Parameter("self", inspect.Parameter.POSITIONAL_OR_KEYWORD),
                    inspect.Parameter(
                        "key", inspect.Parameter.POSITIONAL_OR_KEYWORD, annotation=str
                    ),
                ],
                return_annotation=bytes,
            ),
        )
    elif scenario == "missing-type":
        method.__annotations__.pop("return")
    elif scenario == "unavailable":
        setattr(method, "__signature__", "invalid")
    elif scenario == "mixed":
        method.__annotations__["key"] = bytes
        write = MemoryStorage.write
        other = types.FunctionType(write.__code__, write.__globals__, write.__name__)
        other.__annotations__ = {"key": str, "value": bytes}
        setattr(impl, "write", other)
    elif scenario == "empty":

        class Marker(Protocol):
            pass

        result = Contract(Marker).check(candidate)
        assert str(result).startswith(row["headline"])
        assert result.compatible and result.complete and not result.evidence
        return
    result = contract.check(candidate)
    assert result.status.value == row["status"] and result.complete == row["complete"]
    assert result.accepted() == row["accepted"]["strict"]
    assert result.accepted(strict=False) == row["accepted"]["permissive"]
    assert str(result).startswith(row["headline"])


def test_configuration_types_validated_before_compilation() -> None:
    factory = cast(Callable[..., object], Contract)
    cases: list[dict[str, object]] = [
        {"annotations": 1},
        {"refresh": 1},
        {"globalns": []},
        {"localns": {1: int}},
    ]
    for options in cases:
        with pytest.raises(TypeError):
            factory(int, **options)
