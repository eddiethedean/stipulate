from __future__ import annotations

import threading
import weakref
from typing import Literal, cast

from ._compile import ContractIR, compile_contract
from ._relations import is_class

_lock = threading.RLock()
_cache: dict[
    int,
    tuple[
        weakref.ReferenceType[type[object]],
        dict[tuple[str], weakref.ReferenceType[ContractIR]],
    ],
] = {}


def _drop_declaration(cache_id: int, declaration_ref: weakref.ReferenceType[type[object]]) -> None:
    with _lock:
        entry = _cache.get(cache_id)
        if entry is not None and entry[0] is declaration_ref:
            _cache.pop(cache_id, None)


def get_or_compile(
    declaration: object,
    *,
    policy: Literal["trusted", "raw"],
    globalns: dict[str, object] | None,
    localns: dict[str, object] | None,
    refresh: bool,
) -> ContractIR:
    if not is_class(declaration):
        return compile_contract(declaration, policy=policy, globalns=globalns, localns=localns)
    declaration = cast(type[object], declaration)
    use_cache = globalns is None and localns is None
    key = (policy,)
    if use_cache and not refresh:
        with _lock:
            entry = _cache.get(id(declaration))
            if entry is not None and entry[0]() is declaration:
                ref = entry[1].get(key)
                if ref is not None:
                    ir = ref()
                    if ir is not None:
                        return ir
            elif entry is not None:
                _cache.pop(id(declaration), None)
    ir = compile_contract(declaration, policy=policy, globalns=globalns, localns=localns)
    if use_cache:
        with _lock:
            if not refresh:
                entry = _cache.get(id(declaration))
                if entry is not None and entry[0]() is declaration:
                    ref = entry[1].get(key)
                    existing = None if ref is None else ref()
                    if existing is not None:
                        return existing
            cache_id = id(declaration)
            entry = _cache.get(cache_id)
            if entry is None or entry[0]() is not declaration:

                def on_collect(ref: weakref.ReferenceType[type[object]]) -> None:
                    _drop_declaration(cache_id, ref)

                declaration_ref = weakref.ref(declaration, on_collect)
                values: dict[tuple[str], weakref.ReferenceType[ContractIR]] = {}
                entry = (declaration_ref, values)
                _cache[cache_id] = entry
            entry[1][key] = weakref.ref(ir)
    return ir
