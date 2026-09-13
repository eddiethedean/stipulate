from __future__ import annotations

import ast
import builtins
import importlib
import inspect
import sys
import types
import typing
from collections.abc import Mapping
from typing import Annotated, Callable, Literal, cast

from ._relations import class_dict, form_parts, inspect_missing, unresolved

Policy = Literal["trusted", "raw"]


def _forward_names(value: object, active: frozenset[int] = frozenset()) -> set[str]:
    """Collect possible forward-reference names without evaluating annotations."""
    if id(value) in active:
        return set()
    active = active | {id(value)}
    if isinstance(value, typing.ForwardRef):
        return _forward_names(value.__forward_arg__, active)
    if isinstance(value, str):
        try:
            expression = ast.parse(value, mode="eval")
        except SyntaxError:
            return set()
        expression_names = {node.id for node in ast.walk(expression) if isinstance(node, ast.Name)}
        for node in ast.walk(expression):
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                expression_names.update(_forward_names(node.value, active))
        return expression_names
    origin, args = form_parts(value)
    if origin is Literal:
        return set()
    if origin is Annotated:
        args = args[:1]
    names: set[str] = set()
    for arg in args:
        names.update(_forward_names(arg, active))
    return names


def _contains_unresolved(value: object, active: frozenset[int] = frozenset()) -> bool:
    if value is unresolved:
        return True
    if id(value) in active:
        return False
    origin, args = form_parts(value)
    if origin is Literal:
        return False
    if origin is Annotated:
        args = args[:1]
    return any(_contains_unresolved(arg, active | {id(value)}) for arg in args)


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
    owner: type[object] | None,
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
    locals_map: dict[str, object]
    if owner is None:
        # Plain bindings also guard Python 3.14's optimized ForwardRef lookup,
        # which can bypass dictionary __missing__ hooks. Owner-local precedence
        # cannot be inferred from a global/builtin with the same spelling.
        names = set(globals_map) | set(vars(builtins)) | _forward_names(value)
        locals_map = {name: unresolved for name in names}
    else:
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
        resolved = hints["value"]
        return unresolved if owner is None and _contains_unresolved(resolved) else resolved
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
