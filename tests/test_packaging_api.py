from __future__ import annotations

import importlib.metadata
from typing import Protocol

from typing_extensions import Protocol as ExtensionProtocol

import stipulate
from stipulate import Contract


def test_exports_and_distribution_metadata() -> None:
    assert set(stipulate.__all__) == {
        "Contract",
        "CompatibilityResult",
        "CompatibilityStatus",
        "Evidence",
        "EvidenceStatus",
        "DiagnosticRecord",
        "StipulateError",
        "ContractError",
        "ContractDefinitionError",
    }
    metadata = importlib.metadata.metadata("stipulate")
    assert metadata["Version"] == "0.1.0"
    assert metadata["Requires-Python"] == ">=3.11"
    assert "typing_extensions>=4.15.0" in (metadata.get_all("Requires-Dist") or [])


def test_protocol_roots_and_extensions() -> None:
    assert Contract(Protocol).check(object()).compatible
    assert Contract(ExtensionProtocol).check(object()).compatible

    class Requirement(ExtensionProtocol):
        def f(self) -> int: ...

    class Candidate:
        def f(self) -> int:
            return 1

    assert Contract(Requirement).check(Candidate()).compatible
