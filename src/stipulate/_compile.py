from __future__ import annotations

import inspect
import types
import typing
from dataclasses import dataclass
from typing import Literal, cast

from ._annotations import Policy, annotation_map, declared_annotation
from ._errors import ContractDefinitionError
from ._evidence import Evidence, EvidenceStatus
from ._relations import Unavailable, class_dict, class_mro, is_class, relate, supported
from ._signatures import check_signature, exposed_signature, unbind

Phase = Literal["declaration", "members", "annotations", "types", "inheritance"]


@dataclass(frozen=True, slots=True)
class MethodIR:
    name: str
    signature: inspect.Signature
    coroutine: bool
    owner: type[object]


@dataclass(frozen=True, slots=True)
class AttributeIR:
    name: str
    read_type: object
    write_type: object
    owner: type[object]
    property: bool
    writable: bool


MemberIR = MethodIR | AttributeIR


@dataclass(frozen=True, slots=True, weakref_slot=True)
class ContractIR:
    declaration: type[object]
    name: str
    members: tuple[MemberIR, ...]
    annotations: Policy


def _failure(
    code: str, loc: tuple[str | int, ...], msg: str, phase: Phase
) -> ContractDefinitionError:
    return ContractDefinitionError(
        Evidence(loc, EvidenceStatus.INCOMPATIBLE, code, msg, source="declaration"), phase=phase
    )


def _required(value: object, loc: tuple[str | int, ...]) -> object:
    if type(value) is Unavailable:
        raise _failure(
            "invalid_contract" if value.code == "annotation_missing" else value.code,
            loc,
            "The required annotation is unavailable",
            "annotations",
        )
    if not supported(value):
        raise _failure(
            "unsupported_type", loc, "The required type is outside the 0.1 type table", "types"
        )
    return value


def metadata_safe(cls: type[object]) -> bool:
    meta = type(cls)
    for owner in class_mro(meta):
        hook = class_dict(owner).get("__getattribute__")
        if hook is not None:
            return hook is type.__getattribute__
    return True


def _member(
    owner: type[object],
    name: str,
    policy: Policy,
    globalns: dict[str, object] | None,
    localns: dict[str, object] | None,
) -> MemberIR:
    namespace = class_dict(owner)
    raw = namespace.get(name)
    if type(raw) is types.FunctionType:
        if typing.get_overloads(raw):
            raise _failure(
                "unsupported_type", (name,), "Overloaded methods are unsupported", "members"
            )
        if inspect.isgeneratorfunction(raw) or inspect.isasyncgenfunction(raw):
            raise _failure(
                "invalid_contract", (name,), "Generator methods are unsupported", "members"
            )
        signature = exposed_signature(
            raw, raw=policy == "raw", owner=owner, globalns=globalns, localns=localns
        )
        signature = None if signature is None else unbind(signature)
        if signature is None:
            raise _failure(
                "invalid_contract",
                (name,),
                "A bound method signature is unavailable",
                "members",
            )
        for parameter in signature.parameters.values():
            _required(parameter.annotation, (name, parameter.name))
        _required(signature.return_annotation, (name, "return"))
        return MethodIR(name, signature, inspect.iscoroutinefunction(raw), owner)
    if type(raw) is property:
        if raw.fget is None or not isinstance(raw.fget, types.FunctionType):
            raise _failure("invalid_contract", (name,), "A standard getter is required", "members")
        getter = exposed_signature(
            raw.fget, raw=policy == "raw", owner=owner, globalns=globalns, localns=localns
        )
        getter = None if getter is None else unbind(getter)
        if (
            getter is None
            or getter.parameters
            or inspect.iscoroutinefunction(raw.fget)
            or inspect.isgeneratorfunction(raw.fget)
        ):
            raise _failure(
                "invalid_contract",
                (name,),
                "A property getter must accept only its receiver",
                "members",
            )
        read = _required(
            getter.return_annotation,
            (name, "read"),
        )
        write: object = None
        if raw.fset is not None:
            setter = exposed_signature(
                raw.fset, raw=policy == "raw", owner=owner, globalns=globalns, localns=localns
            )
            setter = None if setter is None else unbind(setter)
            if (
                setter is None
                or len(setter.parameters) != 1
                or next(iter(setter.parameters.values())).kind
                not in (inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD)
                or inspect.iscoroutinefunction(raw.fset)
                or inspect.isgeneratorfunction(raw.fset)
                or inspect.isasyncgenfunction(raw.fset)
            ):
                raise _failure(
                    "invalid_contract", (name,), "A standard setter is required", "members"
                )
            write = _required(next(iter(setter.parameters.values())).annotation, (name, "write"))
            returned = _required(setter.return_annotation, (name, "setter", "return"))
            if returned is not None and returned is not type(None):
                raise _failure(
                    "invalid_contract", (name,), "A setter must declare return None", "members"
                )
        return AttributeIR(name, read, write, owner, True, raw.fset is not None)
    annotations = annotation_map(owner, policy)
    if name in annotations:
        value = _required(
            declared_annotation(owner, owner, name, policy, globalns, localns), (name, "read")
        )
        return AttributeIR(name, value, value, owner, False, True)
    raise _failure(
        "invalid_contract", (name,), "The required member kind is unsupported", "members"
    )


def _satisfies(required: MemberIR, provided: MemberIR) -> bool:
    if isinstance(required, MethodIR):
        return (
            isinstance(provided, MethodIR)
            and required.coroutine == provided.coroutine
            and (
                check_signature(required.signature, provided.signature).status
                is EvidenceStatus.PROVEN
            )
        )
    if not isinstance(provided, AttributeIR) or (required.writable and not provided.writable):
        return False
    if relate(provided.read_type, required.read_type).status is not EvidenceStatus.PROVEN:
        return False
    return not required.writable or (
        relate(required.write_type, provided.write_type).status is EvidenceStatus.PROVEN
    )


def _compile_contract(
    declaration: object,
    *,
    policy: Policy,
    globalns: dict[str, object] | None,
    localns: dict[str, object] | None,
) -> ContractIR:
    if not is_class(declaration):
        raise _failure(
            "invalid_contract",
            (),
            "An actual Protocol with standard metadata is required",
            "declaration",
        )
    declaration = cast(type[object], declaration)
    if not metadata_safe(declaration):
        raise _failure(
            "invalid_contract", (), "Custom metaclass lookup is unsupported", "declaration"
        )
    namespace = class_dict(declaration)
    if not namespace.get("_is_protocol", False):
        raise _failure(
            "invalid_contract", (), "The declaration must explicitly be a Protocol", "declaration"
        )
    if namespace.get("__parameters__", ()) or namespace.get("__type_params__", ()):
        raise _failure("unsupported_type", (), "Generic Protocols are unsupported", "types")
    excluded = set(cast(list[str], getattr(typing, "EXCLUDED_ATTRIBUTES", []))) | {
        "__init__",
        "__new__",
        "__init_subclass__",
        "__class_getitem__",
        "__annotate__",
        "__annotations__",
        "__protocol_attrs__",
        "__non_callable_proto_members__",
        "__static_attributes__",
        "__firstlineno__",
        "__type_params__",
        "__annotate_func__",
        "__annotations_cache__",
    }
    owners: dict[str, list[type[object]]] = {}
    for owner in class_mro(declaration):
        if owner in (object, typing.Protocol, typing.Generic):
            continue
        values = class_dict(owner)
        # The typing_extensions Protocol root has no user obligations.
        if (
            values.get("__module__") == "typing_extensions"
            and type.__getattribute__(owner, "__name__") == "Protocol"
        ):
            continue
        annotations = annotation_map(owner, policy)
        if "__unresolved__" in annotations:
            raise _failure(
                "annotation_unresolved",
                (),
                "Member annotations cannot be obtained under this policy",
                "annotations",
            )
        for name in sorted(set(values) | set(annotations)):
            if name in excluded or name.startswith("_abc_"):
                continue
            owners.setdefault(name, []).append(owner)
    members: list[MemberIR] = []
    for name, declarations in sorted(owners.items()):
        obligations = [_member(owner, name, policy, globalns, localns) for owner in declarations]
        effective = obligations[0]
        if any(not _satisfies(base, effective) for base in obligations[1:]):
            raise _failure(
                "conflicting_member",
                (name,),
                "The effective declaration does not establish every inherited obligation",
                "inheritance",
            )
        members.append(effective)
    return ContractIR(
        declaration,
        cast(str, type.__getattribute__(declaration, "__name__")),
        tuple(members),
        policy,
    )


def compile_contract(
    declaration: object,
    *,
    policy: Policy,
    globalns: dict[str, object] | None,
    localns: dict[str, object] | None,
) -> ContractIR:
    try:
        return _compile_contract(declaration, policy=policy, globalns=globalns, localns=localns)
    except ContractDefinitionError as error:
        name = (
            cast(str, type.__getattribute__(cast(type[object], declaration), "__name__"))
            if is_class(declaration)
            else "contract"
        )
        raise ContractDefinitionError(
            Evidence(
                error.loc,
                EvidenceStatus.INCOMPATIBLE,
                error.code,
                error.msg,
                source="declaration",
                hint=error.hint,
            ),
            phase=error.phase,
            name=name,
        ) from None
