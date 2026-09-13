from __future__ import annotations

from typing import TYPE_CHECKING, Literal

from ._evidence import DiagnosticRecord, Evidence, diagnostic
from ._render import wrapped

if TYPE_CHECKING:
    from ._compatibility import CompatibilityResult

Phase = Literal["declaration", "members", "annotations", "types", "inheritance"]


class StipulateError(Exception):
    """Base class for Stipulate failures."""


class ContractDefinitionError(StipulateError):
    def __init__(
        self, evidence: Evidence, *, phase: Phase = "declaration", name: str = "contract"
    ) -> None:
        self._evidence = evidence
        self._phase: Phase = phase
        self._name = name
        super().__init__(self._render())

    @property
    def code(self) -> str:
        return self._evidence.code

    @property
    def loc(self) -> tuple[str | int, ...]:
        return self._evidence.loc

    @property
    def phase(self) -> Phase:
        return self._phase

    @property
    def msg(self) -> str:
        return self._evidence.msg

    @property
    def hint(self) -> str | None:
        return self._evidence.hint

    def _render(self) -> str:
        location = ".".join(str(part) for part in self.loc) or "<contract>"
        lines = wrapped(f"Cannot compile {self._name} at {location}: {self.msg}")
        if self.hint:
            lines.extend(wrapped(self.hint))
        return "\n".join(lines)


class ContractError(StipulateError):
    def __init__(
        self, result: CompatibilityResult, *, strict: bool, rejected: tuple[Evidence, ...]
    ) -> None:
        self._result = result
        self._strict = strict
        self._rejected = rejected
        super().__init__(
            str(result) + "\n" + f"Rejected by {'strict' if strict else 'permissive'} validation."
        )

    @property
    def result(self) -> CompatibilityResult:
        return self._result

    @property
    def strict(self) -> bool:
        return self._strict

    def errors(self) -> list[DiagnosticRecord]:
        """Return fresh findings responsible for policy rejection."""
        return [diagnostic(item) for item in self._rejected]
