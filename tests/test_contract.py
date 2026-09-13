from __future__ import annotations

from typing import Callable, Protocol, cast

import pytest

from stipulate import (
    CompatibilityStatus,
    Contract,
    ContractDefinitionError,
    ContractError,
)


class Reader(Protocol):
    def read(self, key: str) -> bytes: ...


class Good:
    def read(self, key: str) -> bytes:
        return key.encode()


class Narrow:
    def read(self, key: bytes) -> bytes:
        return key


class Untyped:
    def read(self, key: object) -> bytes:
        return b""


Untyped.read.__annotations__ = {}


def test_validate_returns_original_and_check_is_compatible() -> None:
    contract = Contract(Reader)
    candidate = Good()
    assert contract.contract is contract
    assert contract.validate(candidate) is candidate
    result = contract.check(candidate)
    assert result.status is CompatibilityStatus.COMPATIBLE
    assert result.complete and bool(result)
    assert result.errors() == [] and result.unknowns() == []


def test_known_mismatch_rejects_both_policies() -> None:
    result = Contract(Reader).check(Narrow())
    assert result.status is CompatibilityStatus.INCOMPATIBLE
    assert result.complete
    assert result.errors()[0]["type"] == "parameter_type"
    assert not result.accepted(strict=False)
    with pytest.raises(ContractError) as error:
        Contract(Reader).validate(Narrow())
    assert error.value.result.status is CompatibilityStatus.INCOMPATIBLE


def test_missing_annotation_is_unknown_and_allowlisted() -> None:
    contract = Contract(Reader)
    result = contract.check(Untyped())
    assert result.status is CompatibilityStatus.UNKNOWN
    assert not result.complete and not bool(result)
    assert result.accepted(strict=False)
    with pytest.raises(ContractError):
        contract.validate(Untyped())
    assert contract.validate(Untyped(), strict=False).__class__ is Untyped


def test_invalid_requirement_is_definition_error() -> None:
    class Bad(Protocol):
        def read(self, key: object) -> bytes: ...

    Bad.read.__annotations__ = {"return": bytes}

    with pytest.raises(ContractDefinitionError):
        Contract(Bad)


def test_empty_contract_and_class_candidate() -> None:
    class Marker(Protocol):
        pass

    assert Contract(Marker).check(object()).status is CompatibilityStatus.COMPATIBLE
    assert Contract(Marker).check(Marker).status is CompatibilityStatus.UNKNOWN


def test_configuration_validation() -> None:
    factory = cast(Callable[..., Contract[object]], Contract)
    with pytest.raises(ValueError):
        factory(Reader, annotations="evaluate_safely")
    with pytest.raises(TypeError):
        factory(Reader, refresh=1)
    with pytest.raises(TypeError):
        factory(Reader, globalns={1: int})
