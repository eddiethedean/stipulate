from __future__ import annotations

import math
import unicodedata
from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Literal, Mapping, TypeAlias, TypedDict, cast

JsonValue: TypeAlias = None | bool | int | float | str | list["JsonValue"] | dict[str, "JsonValue"]


class DiagnosticRecord(TypedDict):
    loc: list[str | int]
    type: str
    status: Literal["proven", "incompatible", "unknown"]
    msg: str
    expected: str | None
    actual: str | None
    source: str
    hint: str | None
    ctx: dict[str, JsonValue]


class EvidenceStatus(Enum):
    PROVEN = "proven"
    INCOMPATIBLE = "incompatible"
    UNKNOWN = "unknown"


def _freeze(value: object) -> object:
    if isinstance(value, Mapping):
        values = cast(dict[object, object], value)
        if any(type(k) is not str for k in values):
            raise TypeError("Diagnostic context keys must be strings")
        return MappingProxyType({_safe_text(cast(str, k)): _freeze(v) for k, v in values.items()})
    if isinstance(value, list):
        list_values = cast(list[object], value)
        return tuple(_freeze(v) for v in list_values)
    if isinstance(value, tuple):
        tuple_values = cast(tuple[object, ...], value)
        return tuple(_freeze(v) for v in tuple_values)
    if value is None or type(value) in (bool, int):
        return value
    if type(value) is str:
        return _safe_text(value)
    if type(value) is float and math.isfinite(value):
        return value
    raise TypeError("Diagnostic context must contain finite JSON values")


@dataclass(frozen=True, slots=True, weakref_slot=True)
class Evidence:
    loc: tuple[str | int, ...]
    status: EvidenceStatus
    code: str
    msg: str
    expected: str | None = None
    actual: str | None = None
    source: str = "inspection"
    hint: str | None = None
    ctx: Mapping[str, object] = field(default_factory=lambda: MappingProxyType({}))

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "loc",
            tuple(_safe_text(value) if type(value) is str else value for value in self.loc),
        )
        for field_name in ("code", "msg", "expected", "actual", "source", "hint"):
            value = getattr(self, field_name)
            if type(value) is str:
                object.__setattr__(self, field_name, _safe_text(value))
        object.__setattr__(self, "ctx", cast(Mapping[str, object], _freeze(dict(self.ctx))))


def _safe_text(value: str) -> str:
    result: list[str] = []
    for char in value:
        if unicodedata.category(char).startswith("C"):
            codepoint = ord(char)
            result.append(f"\\u{codepoint:04X}" if codepoint <= 0xFFFF else f"\\U{codepoint:08X}")
        else:
            result.append(char)
    return "".join(result)


def diagnostic(evidence: Evidence) -> DiagnosticRecord:
    return cast(
        DiagnosticRecord,
        {
            "loc": list(evidence.loc),
            "type": evidence.code,
            "status": evidence.status.value,
            "msg": evidence.msg,
            "expected": evidence.expected,
            "actual": evidence.actual,
            "source": evidence.source,
            "hint": evidence.hint,
            "ctx": _thaw(evidence.ctx),
        },
    )


def _thaw(value: object) -> object:
    if isinstance(value, Mapping):
        values = cast(Mapping[object, object], value)
        return {str(k): _thaw(v) for k, v in values.items()}
    if isinstance(value, tuple):
        tuple_values = cast(tuple[object, ...], value)
        return [_thaw(v) for v in tuple_values]
    return value
