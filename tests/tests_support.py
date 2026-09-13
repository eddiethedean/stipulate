from __future__ import annotations

from typing import Callable, Protocol, cast

from stipulate import Contract


def requirement(source: str, extra: dict[str, object] | None = None) -> object:
    namespace: dict[str, object] = {"Protocol": Protocol, "__name__": __name__, **(extra or {})}
    exec(compile(source, "<runtime-fixture>", "exec", dont_inherit=True), namespace)
    return namespace["Requirement"]


def dynamic_contract(value: object, **options: object) -> Contract[object]:
    factory = cast(Callable[..., Contract[object]], Contract)
    return factory(value, **options)
