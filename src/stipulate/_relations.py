from __future__ import annotations

import enum
import types
import typing
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from typing import Annotated, Any, Literal, cast, get_args, get_origin

from ._evidence import EvidenceStatus


@dataclass(frozen=True, slots=True)
class Relation:
    status: EvidenceStatus
    code: str | None = None
    reason: str | None = None
    unknown_codes: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class Unavailable:
    code: str


inspect_missing = Unavailable("annotation_missing")
unresolved = Unavailable("annotation_unresolved")
ORIGINS = (list, set, dict, tuple, Sequence, Mapping, Iterable)


def ok() -> Relation:
    return Relation(EvidenceStatus.PROVEN)


def bad(reason: str = "The declared types are not directionally assignable") -> Relation:
    return Relation(EvidenceStatus.INCOMPATIBLE, reason=reason)


def unknown(code: str = "unsupported_type") -> Relation:
    return Relation(EvidenceStatus.UNKNOWN, code, "The type relation cannot be established")


def all_of(items: Iterable[Relation]) -> Relation:
    values = tuple(items)
    codes = tuple(
        dict.fromkeys(
            code
            for v in values
            for code in (
                *((v.code or "unsupported_type",) if v.status is EvidenceStatus.UNKNOWN else ()),
                *v.unknown_codes,
            )
        )
    )
    for status in (EvidenceStatus.INCOMPATIBLE, EvidenceStatus.UNKNOWN):
        found = next((v for v in values if v.status is status), None)
        if found is not None:
            return Relation(found.status, found.code, found.reason, codes)
    return ok()


def any_of(items: Iterable[Relation]) -> Relation:
    values = tuple(items)
    for status in (EvidenceStatus.PROVEN, EvidenceStatus.UNKNOWN):
        found = next((v for v in values if v.status is status), None)
        if found is not None:
            return found
    return bad()


def class_dict(cls: type[object]) -> Mapping[str, object]:
    return cast(Mapping[str, object], type.__getattribute__(cls, "__dict__"))


def class_mro(cls: type[object]) -> tuple[type[object], ...]:
    return cast(tuple[type[object], ...], type.__getattribute__(cls, "__mro__"))


def is_class(value: object) -> bool:
    return any(base is type for base in class_mro(type(value)))


def form_parts(value: object) -> tuple[object, tuple[object, ...]]:
    if is_class(value):
        return None, ()
    cls = type(value)
    module = type.__getattribute__(cls, "__module__")
    is_generic_alias = any(cls is generic for generic in (types.GenericAlias, types.UnionType))
    if not is_generic_alias and module not in (
        "typing",
        "typing_extensions",
    ):
        return None, ()
    return get_origin(value), get_args(value)


def supported(value: object, active: frozenset[int] = frozenset()) -> bool:
    if id(value) in active:
        return False
    active = active | {id(value)}
    if value is None or value is Any:
        return True
    origin, args = form_parts(value)
    if origin is Annotated:
        return bool(args) and supported(args[0], active)
    if any(origin is o for o in (typing.Union, types.UnionType)):
        return bool(args) and all(supported(a, active) for a in args)
    if origin is Literal:
        return bool(args) and all(
            type(a) in (int, bool, str, bytes, type(None)) or enum.Enum in class_mro(type(a))
            for a in args
        )
    if any(origin is o for o in ORIGINS):
        if origin is tuple:
            if len(args) == 2 and args[1] is Ellipsis:
                return supported(args[0], active)
            return all(a is not Ellipsis and supported(a, active) for a in args)
        count = 2 if origin is dict or origin is Mapping else 1
        return (not args or len(args) == count) and all(supported(a, active) for a in args)
    if origin is not None:
        return False
    if is_class(value):
        value = cast(type[object], value)
        namespace = class_dict(value)
        return (
            not namespace.get("_is_protocol", False)
            and not namespace.get("__parameters__", ())
            and not namespace.get("__type_params__", ())
        )
    return False


def _nominal(source: type[object], destination: type[object]) -> Relation:
    if any(destination is base for base in class_mro(source)):
        return ok()
    source_is_int = any(base is int for base in class_mro(source))
    source_is_float = any(base is float for base in class_mro(source))
    if source_is_int and any(destination is target for target in (float, complex)):
        return ok()
    if source_is_float and destination is complex:
        return ok()
    routes: dict[type[object], tuple[type[object], ...]] = {
        list: (Sequence, Iterable),
        tuple: (Sequence, Iterable),
        set: (Iterable,),
        dict: (Mapping, Iterable),
        Mapping: (Iterable,),
        Sequence: (Iterable,),
        str: (Sequence, Iterable),
        bytes: (Sequence, Iterable),
        bytearray: (Sequence, Iterable),
    }
    return (
        ok()
        if any(
            any(destination is route for route in routes_for(routes, base))
            for base in class_mro(source)
        )
        else bad()
    )


def routes_for(
    routes: dict[type[object], tuple[type[object], ...]], key: type[object]
) -> tuple[type[object], ...]:
    for route_key, values in routes.items():
        if route_key is key:
            return values
    return ()


def relate(source: object, destination: object) -> Relation:
    # Supportedness precedes shortcuts, including object and identity.
    for value in (source, destination):
        if type(value) is not Unavailable and not supported(value):
            return unknown()
    for value in (source, destination):
        if type(value) is Unavailable:
            return unknown(value.code)
    if source is None:
        source = type(None)
    if destination is None:
        destination = type(None)
    if destination is typing.Tuple:
        destination = tuple
    so, sa = form_parts(source)
    do, da = form_parts(destination)
    if so is Annotated:
        return relate(sa[0], destination)
    if do is Annotated:
        return relate(source, da[0])
    if any(so is o for o in (typing.Union, types.UnionType)):
        return all_of(relate(a, destination) for a in sa)
    if any(do is o for o in (typing.Union, types.UnionType)):
        return any_of(relate(source, a) for a in da)
    if destination is object:
        return ok()
    if source is Any or destination is Any:
        return unknown("gradual_type")
    if so is Literal:
        if do is Literal:
            return all_of(ok() if any(_literal_equal(a, b) for b in da) else bad() for a in sa)
        return all_of(relate(type(a), destination) for a in sa)
    if do is Literal:
        return bad()
    sb = cast(type[object], so or source)
    db = cast(type[object], do or destination)
    if do is None:
        return _nominal(sb, db)
    if (
        so is None
        and any(source is c for c in (str, bytes, bytearray))
        and any(do is o for o in (Sequence, Iterable))
    ):
        return relate(str if source is str else int, da[0]) if da else ok()
    routes: dict[type[object], tuple[type[object], ...]] = {
        list: (list, Sequence, Iterable),
        set: (set, Iterable),
        dict: (dict, Mapping, Iterable),
        tuple: (tuple, Sequence, Iterable),
        Sequence: (Sequence, Iterable),
        Mapping: (Mapping, Iterable),
        Iterable: (Iterable,),
    }
    if not any(db is route for route in routes_for(routes, sb)):
        if so is None and any(
            any(db is route for route in routes_for(routes, base)) for base in class_mro(sb)
        ):
            return unknown("unsupported_type")
        return bad()
    if not da and do is not tuple:
        return ok()
    # tuple[()] is a fixed empty tuple; a bare tuple erases its length/element type.
    if (not sa and not (so is tuple and source is not typing.Tuple)) or (
        so is None or source is typing.Tuple
    ):
        return unknown("gradual_type")
    if sb is tuple:
        homogeneous = len(sa) == 2 and sa[1] is Ellipsis
        if db is tuple:
            if len(da) == 2 and da[1] is Ellipsis:
                return all_of(relate(a, da[0]) for a in (sa[:1] if homogeneous else sa))
            if homogeneous:
                return bad("A homogeneous tuple cannot establish a fixed length")
            if len(sa) != len(da):
                return bad("Tuple lengths are incompatible")
            return all_of(relate(a, b) for a, b in zip(sa, da))
        return all_of(relate(a, da[0]) for a in (sa[:1] if homogeneous else sa))
    if db is Iterable:
        return relate(sa[0], da[0])
    if any(db is container for container in (list, set, dict)):
        return all_of(all_of((relate(a, b), relate(b, a))) for a, b in zip(sa, da))
    if db is Mapping:
        return all_of((relate(sa[0], da[0]), relate(da[0], sa[0]), relate(sa[1], da[1])))
    return relate(sa[0], da[0])


def _literal_equal(a: object, b: object) -> bool:
    if type(a) is not type(b):
        return False
    if enum.Enum in class_mro(type(a)):
        return a is b
    return a == b


def type_label(value: object) -> str | None:
    """Render only known type structure; never repr user values or metadata."""
    if type(value) is Unavailable:
        return None
    if value is None:
        return "None"
    if value is Any:
        return "Any"
    if is_class(value):
        value = cast(type[object], value)
        return cast(str, type.__getattribute__(value, "__name__"))
    origin, args = form_parts(value)
    if origin is Annotated:
        return type_label(args[0])
    if any(origin is o for o in (typing.Union, types.UnionType)):
        return " | ".join(type_label(a) or "unavailable" for a in args)
    if origin is Literal:
        return "Literal[" + ", ".join(_literal_label(a) for a in args) + "]"
    if any(origin is o for o in ORIGINS):
        return (
            (type_label(origin) or "container")
            + "["
            + ", ".join("..." if a is Ellipsis else type_label(a) or "unsupported" for a in args)
            + "]"
        )
    return "unsupported type"


def _literal_label(value: object) -> str:
    if type(value) in (int, bool, str, bytes, type(None)):
        return repr(value)
    if enum.Enum in class_mro(type(value)):
        return (type_label(type(value)) or "Enum") + " member"
    return "unsupported literal"
