from __future__ import annotations

import importlib
import inspect
import sys
import types
import typing
from collections.abc import Mapping
from typing import Callable, Literal, cast

from ._relations import class_dict, inspect_missing, unresolved

Policy = Literal["trusted", "raw"]


def _materialized(value: object) -> Mapping[str, object]:
    if type(value) is not dict:
        return {"__unresolved__": unresolved}
    return cast(dict[str, object], value)


def annotation_map(obj: types.FunctionType | type[object], policy: Policy) -> Mapping[str, object]:
    if isinstance(obj, types.FunctionType):
        # Reading __annotate__ does not invoke it. Reading __annotations__ can.
        if policy == "raw" and getattr(obj, "__annotate__", None) is not None:
            return {"__unresolved__": unresolved}
        try:
            if getattr(obj, "__annotate__", None) is not None:
                library = importlib.import_module("annotationlib")
                getter = cast(Callable[..., Mapping[str, object]], library.get_annotations)
                return getter(obj, format=library.Format.STRING)
            return _materialized(obj.__annotations__)
        except Exception:
            # Exactly the annotation-factory boundary, not an engine-wide catch.
            return {"__unresolved__": unresolved}
    namespace = class_dict(obj)
    if "__annotations__" in namespace:
        return _materialized(namespace["__annotations__"])
    if "__annotations_cache__" in namespace:
        return _materialized(namespace["__annotations_cache__"])
    if namespace.get("__annotate__") is not None or namespace.get("__annotate_func__") is not None:
        if policy == "raw":
            return {"__unresolved__": unresolved}
        try:
            library = importlib.import_module("annotationlib")
            getter = cast(Callable[..., Mapping[str, object]], library.get_annotations)
            return getter(obj, format=library.Format.STRING)
        except Exception:
            return {"__unresolved__": unresolved}
    return {}


def resolve(
    value: object,
    obj: types.FunctionType | type[object],
    owner: type[object],
    policy: Policy,
    globalns: Mapping[str, object] | None = None,
    localns: Mapping[str, object] | None = None,
) -> object:
    if value is inspect.Signature.empty:
        return inspect_missing
    if value is unresolved or value is inspect_missing:
        return value
    if policy == "raw":
        return unresolved if isinstance(value, (str, typing.ForwardRef)) else value
    globals_map: dict[str, object]
    if isinstance(obj, types.FunctionType):
        globals_map = dict(obj.__globals__)
    else:
        module = sys.modules.get(cast(str, class_dict(obj).get("__module__", "")))
        globals_map = {} if module is None else dict(vars(module))
    globals_map.update(globalns or {})
    locals_map = dict(class_dict(owner))
    locals_map[cast(str, type.__getattribute__(owner, "__name__"))] = owner
    locals_map.update(localns or {})

    # A one-annotation carrier resolves each expression independently, with extras.
    def carrier() -> None:
        pass

    carrier.__annotations__ = {"value": value}
    try:
        hints = typing.get_type_hints(
            carrier, globalns=globals_map, localns=locals_map, include_extras=True
        )
        return hints["value"]
    except Exception:
        return unresolved


def declared_annotation(
    obj: types.FunctionType | type[object],
    owner: type[object],
    name: str,
    policy: Policy,
    globalns: Mapping[str, object] | None = None,
    localns: Mapping[str, object] | None = None,
) -> object:
    values = annotation_map(obj, policy)
    value = values.get(name, values.get("__unresolved__", inspect_missing))
    return resolve(value, obj, owner, policy, globalns, localns)
