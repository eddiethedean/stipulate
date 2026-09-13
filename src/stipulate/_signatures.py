from __future__ import annotations

import inspect
import itertools
import types
from collections.abc import Mapping
from dataclasses import dataclass

from ._annotations import Policy, annotation_map, resolve
from ._evidence import EvidenceStatus
from ._relations import Relation, all_of, inspect_missing, relate


@dataclass(frozen=True, slots=True)
class SignatureCheck:
    status: EvidenceStatus
    message: str = ""
    code: str = "signature"
    parameter_relations: tuple[tuple[str, Relation], ...] = ()
    return_relation: Relation | None = None
    routes: tuple[tuple[str, str], ...] = ()
    failed_call: tuple[int, tuple[str, ...]] | None = None
    shape_status: EvidenceStatus = EvidenceStatus.PROVEN


def exposed_signature(
    obj: object,
    *,
    raw: bool,
    owner: type[object] | None = None,
    globalns: dict[str, object] | None = None,
    localns: dict[str, object] | None = None,
) -> inspect.Signature | None:
    """Select one metadata layer, recover shape without annotation evaluation."""
    target = obj
    seen: set[int] = set()
    selected: inspect.Signature | None = None
    explicit_layer = False
    while True:
        if id(target) in seen or type(target) is not types.FunctionType:
            return None
        seen.add(id(target))
        explicit = inspect.getattr_static(target, "__signature__", None)
        if explicit is not None:
            if type(explicit) is not inspect.Signature:
                return None
            try:
                if any(type(p) is not inspect.Parameter for p in explicit.parameters.values()):
                    return None
                selected = inspect.Signature(
                    tuple(explicit.parameters.values()),
                    return_annotation=explicit.return_annotation,
                )
            except (TypeError, ValueError):
                return None
            explicit_layer = True
            break
        wrapped = inspect.getattr_static(target, "__wrapped__", None)
        if wrapped is None:
            clone = types.FunctionType(
                target.__code__,
                target.__globals__,
                target.__name__,
                target.__defaults__,
                target.__closure__,
            )
            clone.__kwdefaults__ = target.__kwdefaults__
            try:
                selected = inspect.signature(clone, follow_wrapped=False, eval_str=False)
            except (TypeError, ValueError):
                return None
            break
        target = wrapped
    policy: Policy = "raw" if raw else "trusted"
    annotations: Mapping[str, object] = {} if explicit_layer else annotation_map(target, policy)
    if owner is None:
        owner = object
    params: list[inspect.Parameter] = []
    for p in selected.parameters.values():
        value = (
            p.annotation
            if explicit_layer
            else annotations.get(p.name, annotations.get("__unresolved__", inspect_missing))
        )
        params.append(
            p.replace(annotation=resolve(value, target, owner, policy, globalns, localns))
        )
    value = (
        selected.return_annotation
        if explicit_layer
        else annotations.get("return", annotations.get("__unresolved__", inspect_missing))
    )
    return selected.replace(
        parameters=params,
        return_annotation=resolve(value, target, owner, policy, globalns, localns),
    )


def unbind(signature: inspect.Signature) -> inspect.Signature | None:
    params = list(signature.parameters.values())
    if not params or params[0].kind not in (
        inspect.Parameter.POSITIONAL_ONLY,
        inspect.Parameter.POSITIONAL_OR_KEYWORD,
    ):
        return None
    return signature.replace(parameters=params[1:])


def _bind_routes(
    sig: inspect.Signature, args: tuple[object, ...], kwargs: dict[str, object]
) -> dict[object, str]:
    # inspect.bind on 3.11-3.13 rejects a keyword matching an omitted optional
    # positional-only name, even with **kwargs. Python itself accepts that call.
    # Route according to the language binder, retaining token identities.
    params = sig.parameters
    positional = [
        p for p in params.values() if p.kind in (p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD)
    ]
    varargs = next((p for p in params.values() if p.kind is p.VAR_POSITIONAL), None)
    varkw = next((p for p in params.values() if p.kind is p.VAR_KEYWORD), None)
    routed: dict[object, str] = {}
    assigned: set[str] = set()
    for i, token in enumerate(args):
        parameter = positional[i] if i < len(positional) else varargs
        if parameter is None:
            raise TypeError("too many positional arguments")
        routed[token] = parameter.name
        assigned.add(parameter.name)
    for name, token in kwargs.items():
        parameter = params.get(name)
        if parameter is not None and parameter.kind in (
            parameter.POSITIONAL_OR_KEYWORD,
            parameter.KEYWORD_ONLY,
        ):
            if name in assigned:
                raise TypeError("duplicate argument")
            assigned.add(name)
        else:
            parameter = varkw
            if parameter is None:
                raise TypeError("unexpected keyword")
        routed[token] = parameter.name
    for parameter in params.values():
        if (
            parameter.kind not in (parameter.VAR_POSITIONAL, parameter.VAR_KEYWORD)
            and parameter.default is parameter.empty
            and parameter.name not in assigned
        ):
            raise TypeError("missing required argument")
    return routed


def check_signature(required: inspect.Signature, provided: inspect.Signature) -> SignatureCheck:
    """Exact finite call partition: positional boundary and all keyword subsets.

    Beyond B named positional routing is stable. Names outside K share the
    variadic-keyword route; one fresh name represents that equivalence class.
    Tokens carry argument identity only and never invoke a user callable.
    """
    positional = (inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD)
    boundary = max(
        sum(p.kind in positional for p in sig.parameters.values()) for sig in (required, provided)
    )
    names = sorted(set(required.parameters) | set(provided.parameters))
    fresh = "__stipulate_fresh__"
    while fresh in names:
        fresh += "_"
    names.append(fresh)
    has_tail = any(p.kind is p.VAR_POSITIONAL for p in required.parameters.values())
    routed: set[tuple[str, str]] = set()
    failed: tuple[int, tuple[str, ...]] | None = None
    # Enumerate all legal required classes even after a shape failure: independent
    # annotation mismatches must survive alongside a blocked shape obligation.
    req_pos = [p for p in required.parameters.values() if p.kind in positional]
    req_varkw = any(p.kind is p.VAR_KEYWORD for p in required.parameters.values())
    for count in range(boundary + 1 + int(has_tail)):
        if count > len(req_pos) and not has_tail:
            continue
        if any(p.kind is p.POSITIONAL_ONLY and p.default is p.empty for p in req_pos[count:]):
            continue
        assigned = {p.name for p in req_pos[:count] if p.kind is p.POSITIONAL_OR_KEYWORD}
        allowed = (
            set(names)
            if req_varkw
            else {
                p.name
                for p in required.parameters.values()
                if p.kind in (p.POSITIONAL_OR_KEYWORD, p.KEYWORD_ONLY)
            }
        )
        allowed -= assigned
        mandatory = {
            p.name
            for p in (*req_pos[count:], *required.parameters.values())
            if p.default is p.empty
            and (
                p.kind is p.KEYWORD_ONLY
                or (p.kind is p.POSITIONAL_OR_KEYWORD and p.name not in assigned)
            )
        }
        optional = [name for name in names if name in allowed and name not in mandatory]
        for mask in itertools.product((False, True), repeat=len(optional)):
            keys = tuple(sorted(mandatory | {k for k, present in zip(optional, mask) if present}))
            args = tuple(object() for _ in range(count))
            kwargs = {k: object() for k in keys}
            try:
                req_routes = _bind_routes(required, args, kwargs)
            except TypeError:
                continue
            try:
                got_routes = _bind_routes(provided, args, kwargs)
            except TypeError:
                if failed is None:
                    failed = (count, keys)
                continue
            routed.update((name, got_routes[token]) for token, name in req_routes.items())
    order = {name: i for i, name in enumerate(required.parameters)}
    routes = tuple(sorted(routed, key=lambda pair: (order[pair[0]], pair[1])))
    relations = tuple(
        (name, relate(required.parameters[name].annotation, provided.parameters[got].annotation))
        for name, got in routes
    )
    rr = relate(provided.return_annotation, required.return_annotation)
    shape = EvidenceStatus.PROVEN if failed is None else EvidenceStatus.INCOMPATIBLE
    total = all_of((Relation(shape), *(r for _, r in relations), rr))
    return SignatureCheck(
        total.status,
        "The implementation rejects a legal required call" if failed else "",
        parameter_relations=relations,
        return_relation=rr,
        routes=routes,
        failed_call=failed,
        shape_status=shape,
    )
