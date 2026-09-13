from __future__ import annotations

from typing import Generic, Literal, Mapping, TypeVar, cast

from typing_extensions import TypeForm

from ._cache import get_or_compile
from ._compatibility import CompatibilityResult
from ._compile import ContractIR
from ._errors import ContractError
from ._render import safe

T = TypeVar("T")


def _annotation_policy(value: object) -> Literal["trusted", "raw"]:
    if not isinstance(value, str):
        raise TypeError("annotations must be a string")
    if value not in ("trusted", "raw"):
        raise ValueError("annotations must be 'trusted' or 'raw'")
    return "trusted" if value == "trusted" else "raw"


def _check_namespace(value: object, name: str) -> None:
    if not isinstance(value, Mapping):
        raise TypeError(f"{name} must be a mapping")
    keys = cast(Mapping[object, object], value)
    if any(not isinstance(key, str) for key in keys):
        raise TypeError(f"{name} keys must be strings")


class Contract(Generic[T]):
    def __init__(
        self,
        declaration: TypeForm[T],
        *,
        annotations: Literal["trusted", "raw"] = "trusted",
        globalns: Mapping[str, object] | None = None,
        localns: Mapping[str, object] | None = None,
        refresh: bool = False,
    ) -> None:
        policy = _annotation_policy(annotations)
        if type(refresh) is not bool:
            raise TypeError("refresh must be a bool")
        for name, namespace in (("globalns", globalns), ("localns", localns)):
            if namespace is not None:
                _check_namespace(namespace, name)
        self._ir: ContractIR = get_or_compile(
            cast(type[object], declaration),
            policy=policy,
            globalns=None if globalns is None else dict(globalns),
            localns=None if localns is None else dict(localns),
            refresh=refresh,
        )

    @property
    def contract(self) -> Contract[T]:
        return self

    def check(self, candidate: object) -> CompatibilityResult:
        from ._compatibility import inspect_candidate

        return inspect_candidate(self._ir, candidate)

    def validate(self, candidate: object, *, strict: bool = True) -> T:
        if type(strict) is not bool:
            raise TypeError("strict must be a bool")
        result = self.check(candidate)
        if not result.accepted(strict=strict):
            rejected = tuple(
                item
                for item in result.evidence
                if item.status.value == "incompatible"
                or (
                    item.status.value == "unknown"
                    and (strict or item.code not in {"annotation_missing", "gradual_type"})
                )
            )
            raise ContractError(result, strict=strict, rejected=rejected)
        return cast(T, candidate)

    def __repr__(self) -> str:
        return f"Contract[{safe(self._ir.name)}]"
