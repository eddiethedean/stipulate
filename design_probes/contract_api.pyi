from collections.abc import Mapping
from enum import Enum
from typing import Generic, Literal, TypeAlias, TypedDict, TypeVar
from typing_extensions import TypeForm

T = TypeVar("T")

class CompatibilityStatus(Enum):
    COMPATIBLE = "compatible"
    INCOMPATIBLE = "incompatible"
    UNKNOWN = "unknown"

_JsonValue: TypeAlias = (
    None | bool | int | float | str | list["_JsonValue"] | dict[str, "_JsonValue"]
)

class DiagnosticRecord(TypedDict):
    loc: list[str | int]
    type: str
    status: Literal["proven", "incompatible", "unknown"]
    msg: str
    expected: str | None
    actual: str | None
    source: str
    hint: str | None
    ctx: dict[str, _JsonValue]

class EvidenceStatus(Enum):
    PROVEN = "proven"
    INCOMPATIBLE = "incompatible"
    UNKNOWN = "unknown"

class Evidence:
    @property
    def loc(self) -> tuple[str | int, ...]: ...
    @property
    def status(self) -> EvidenceStatus: ...
    @property
    def code(self) -> str: ...

class CompatibilityResult:
    @property
    def status(self) -> CompatibilityStatus: ...
    @property
    def compatible(self) -> bool: ...
    @property
    def complete(self) -> bool: ...
    @property
    def evidence(self) -> tuple[Evidence, ...]: ...
    def errors(self) -> list[DiagnosticRecord]: ...
    def unknowns(self) -> list[DiagnosticRecord]: ...
    def __str__(self) -> str: ...
    def __repr__(self) -> str: ...
    def __bool__(self) -> bool: ...
    def accepted(self, *, strict: bool = True) -> bool: ...

class Contract(Generic[T]):
    def __init__(
        self,
        declaration: TypeForm[T],
        *,
        annotations: Literal["trusted", "raw"] = "trusted",
        globalns: Mapping[str, object] | None = None,
        localns: Mapping[str, object] | None = None,
        refresh: bool = False,
    ) -> None: ...
    def __repr__(self) -> str: ...
    def validate(self, candidate: object, *, strict: bool = True) -> T: ...
    def check(self, candidate: object) -> CompatibilityResult: ...
    @property
    def contract(self) -> Contract[T]: ...
