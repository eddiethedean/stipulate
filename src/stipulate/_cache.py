from __future__ import annotations

import threading
import weakref
from typing import Literal, cast

from ._compile import ContractIR, compile_contract
from ._relations import is_class

_lock = threading.RLock()
_cache: weakref.WeakKeyDictionary[
    type[object], dict[tuple[str], weakref.ReferenceType[ContractIR]]
] = weakref.WeakKeyDictionary()


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
            ref = _cache.get(declaration, {}).get(key)
            if ref is not None:
                ir = ref()
                if ir is not None:
                    return ir
    ir = compile_contract(declaration, policy=policy, globalns=globalns, localns=localns)
    if use_cache:
        with _lock:
            if not refresh:
                ref = _cache.get(declaration, {}).get(key)
                existing = None if ref is None else ref()
                if existing is not None:
                    return existing
            _cache.setdefault(declaration, {})[key] = weakref.ref(ir)
    return ir
