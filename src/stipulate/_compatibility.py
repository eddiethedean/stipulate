from __future__ import annotations

import inspect
import types
import typing
from dataclasses import dataclass
from enum import Enum
from typing import cast

from ._annotations import Policy, annotation_map, declared_annotation
from ._compile import AttributeIR, ContractIR, MemberIR, MethodIR, metadata_safe
from ._evidence import DiagnosticRecord, Evidence, EvidenceStatus, diagnostic
from ._relations import (
    Relation,
    Unavailable,
    class_dict,
    class_mro,
    inspect_missing,
    relate,
    type_label,
)
from ._render import render_result
from ._signatures import check_signature, exposed_signature, unbind


class CompatibilityStatus(Enum):
    COMPATIBLE = "compatible"
    INCOMPATIBLE = "incompatible"
    UNKNOWN = "unknown"


@dataclass(frozen=True, slots=True)
class CompatibilityResult:
    _contract_name: str
    evidence: tuple[Evidence, ...]
    _member_count: int = 0

    @property
    def status(self) -> CompatibilityStatus:
        if any(item.status is EvidenceStatus.INCOMPATIBLE for item in self.evidence):
            return CompatibilityStatus.INCOMPATIBLE
        if any(item.status is EvidenceStatus.UNKNOWN for item in self.evidence):
            return CompatibilityStatus.UNKNOWN
        return CompatibilityStatus.COMPATIBLE

    @property
    def compatible(self) -> bool:
        return self.status is CompatibilityStatus.COMPATIBLE

    @property
    def complete(self) -> bool:
        return not any(item.status is EvidenceStatus.UNKNOWN for item in self.evidence)

    def errors(self) -> list[DiagnosticRecord]:
        """Return fresh diagnostics for disproven obligations only."""
        return [diagnostic(i) for i in self.evidence if i.status is EvidenceStatus.INCOMPATIBLE]

    def unknowns(self) -> list[DiagnosticRecord]:
        """Return fresh diagnostics for uncertain and blocked obligations."""
        return [diagnostic(i) for i in self.evidence if i.status is EvidenceStatus.UNKNOWN]

    def accepted(self, *, strict: bool = True) -> bool:
        if type(strict) is not bool:
            raise TypeError("strict must be a bool")
        return self.compatible or (
            not strict
            and self.status is CompatibilityStatus.UNKNOWN
            and all(
                i.code in {"annotation_missing", "gradual_type"}
                for i in self.evidence
                if i.status is EvidenceStatus.UNKNOWN
            )
        )

    def __bool__(self) -> bool:
        return self.compatible

    def __repr__(self) -> str:
        return (
            f"CompatibilityResult(status={self.status.value!r}, complete={self.complete!r}, "
            f"errors={len(self.errors())}, unknowns={len(self.unknowns())})"
        )

    def __str__(self) -> str:
        return render_result(
            self._contract_name, self.status.value, self.evidence, self._member_count
        )


def _fact(
    loc: tuple[str | int, ...],
    status: EvidenceStatus,
    code: str,
    msg: str,
    expected: object = inspect_missing,
    actual: object = inspect_missing,
    source: str = "inspection",
    ctx: dict[str, object] | None = None,
) -> Evidence:
    hint = None
    if status is EvidenceStatus.UNKNOWN and code in {"annotation_missing", "gradual_type"}:
        hint = "Add precise annotations, or explicitly accept type uncertainty with strict=False."
    return Evidence(
        loc, status, code, msg, type_label(expected), type_label(actual), source, hint, ctx or {}
    )


def _relation(
    loc: tuple[str | int, ...],
    relation: Relation,
    code: str,
    expected: object,
    actual: object,
    ctx: dict[str, object] | None = None,
) -> Evidence:
    message = relation.reason or "The declared types do not satisfy this obligation"
    if relation.status is EvidenceStatus.INCOMPATIBLE:
        message = (
            "The implementation input is too narrow for required caller values"
            if code == "parameter_type" or loc[-1] == "write"
            else "The implementation output does not fit the required type"
        )
    return _fact(
        loc,
        relation.status,
        relation.code or code,
        "The declared types satisfy this obligation"
        if relation.status is EvidenceStatus.PROVEN
        else message,
        expected,
        actual,
        "annotation",
        ctx,
    )


def _uncertainties(loc: tuple[str | int, ...], relation: Relation) -> list[Evidence]:
    return [
        _fact(
            loc,
            EvidenceStatus.UNKNOWN,
            code,
            "An independent type branch remains uncertain",
            source="annotation",
            ctx={"independent_branch": True},
        )
        for code in relation.unknown_codes
        if code != relation.code
    ]


def _lookup(cls: type[object], name: str) -> tuple[object, type[object]]:
    for owner in class_mro(cls):
        namespace = class_dict(owner)
        if name in namespace:
            return namespace[name], owner
    return inspect_missing, cls


def _blocked(member: MemberIR, root: tuple[str | int, ...]) -> list[Evidence]:
    suffixes = (
        ["kind", "signature", *member.signature.parameters, "return"]
        if isinstance(member, MethodIR)
        else ["read", *(["write"] if member.writable else [])]
    )
    return [
        _fact(
            (member.name, s),
            EvidenceStatus.UNKNOWN,
            "dependency_unassessed",
            "This obligation is blocked by unavailable member metadata",
            ctx={"root_loc": list(root)},
        )
        for s in suffixes
    ]


def _instance_dict(candidate: object) -> dict[str, object] | Unavailable | None:
    raw, _ = _lookup(type(candidate), "__dict__")
    if type(raw) is not types.GetSetDescriptorType:
        return None
    # This is the standard instance-dictionary descriptor, never a user property.
    try:
        return cast(dict[str, object], raw.__get__(candidate, type(candidate)))
    except (TypeError, ValueError):
        return Unavailable("descriptor_unverifiable")


def _has_descriptor(raw: object) -> bool:
    return any("__get__" in class_dict(c) for c in class_mro(type(raw)))


def inspect_candidate(ir: ContractIR, candidate: object) -> CompatibilityResult:
    if any(base is type for base in class_mro(type(candidate))):
        return CompatibilityResult(
            ir.name,
            (
                _fact(
                    (),
                    EvidenceStatus.UNKNOWN,
                    "unsupported_candidate",
                    "Class-object candidates are unsupported",
                ),
            ),
            len(ir.members),
        )
    if not ir.members:
        return CompatibilityResult(ir.name, (), 0)
    findings: list[Evidence] = []
    cls = type(candidate)
    lookup, lookup_owner = _lookup(cls, "__getattribute__")
    builtin_lookup = lookup_owner in (
        int,
        bool,
        float,
        complex,
        str,
        bytes,
        bytearray,
        list,
        set,
        frozenset,
        dict,
        tuple,
    )
    standard_lookup = lookup is object.__getattribute__ or (
        builtin_lookup
        and type(lookup) is types.WrapperDescriptorType
        and lookup.__objclass__ is lookup_owner
    )
    unsafe = not metadata_safe(cls) or not standard_lookup
    dynamic = _lookup(cls, "__getattr__")[0] is not inspect_missing
    instance = None if unsafe else _instance_dict(candidate)
    if isinstance(instance, Unavailable):
        root = ("__dict__",)
        findings = [
            _fact(
                root,
                EvidenceStatus.UNKNOWN,
                instance.code,
                "The instance dictionary descriptor cannot be inspected for this candidate",
            )
        ]
        for member in ir.members:
            findings.extend(_blocked(member, root))
        return CompatibilityResult(ir.name, tuple(findings), len(ir.members))
    instance_dict = instance
    write_hook = _lookup(cls, "__setattr__")[0]
    write_dynamic = write_hook is not inspect_missing and write_hook is not object.__setattr__
    for member in ir.members:
        root = (member.name,)
        if unsafe:
            findings.append(
                _fact(
                    root,
                    EvidenceStatus.UNKNOWN,
                    "dynamic_member_unverifiable",
                    "Custom lookup prevents a static capability proof",
                )
            )
            findings.extend(_blocked(member, root))
            continue
        raw, owner = _lookup(cls, member.name)
        # Data properties take precedence over instance storage. Ordinary class
        # functions can be shadowed by instance values, which do not bind methods.
        in_instance = instance_dict is not None and member.name in instance_dict
        if raw is inspect_missing and not in_instance:
            code = "dynamic_member_unverifiable" if dynamic else "missing_member"
            status = EvidenceStatus.UNKNOWN if dynamic else EvidenceStatus.INCOMPATIBLE
            findings.append(
                _fact(root, status, code, "The required member has no established static presence")
            )
            findings.extend(_blocked(member, root))
            continue
        if (
            raw is not inspect_missing
            and type(raw) is not property
            and _has_descriptor(raw)
            and type(raw) is not types.FunctionType
        ):
            findings.append(
                _fact(
                    root,
                    EvidenceStatus.UNKNOWN,
                    "descriptor_unverifiable",
                    "The descriptor requires execution to establish this capability",
                )
            )
            findings.extend(_blocked(member, root))
            continue
        findings.append(
            _fact(
                root,
                EvidenceStatus.PROVEN,
                "missing_member",
                "Static member presence is established",
            )
        )
        if isinstance(member, MethodIR):
            if (
                type(raw) is not types.FunctionType
                and type(raw) is not property
                and not _has_descriptor(raw)
                and _lookup(type(raw), "__call__")[0] is inspect_missing
            ):
                findings.append(
                    _fact(
                        (member.name, "kind"),
                        EvidenceStatus.INCOMPATIBLE,
                        "member_kind",
                        "The statically stored member is not callable",
                    )
                )
                findings.extend(_blocked(member, (member.name, "kind")))
                continue
            if type(raw) is types.FunctionType and typing.get_overloads(raw):
                findings.append(
                    _fact(
                        root,
                        EvidenceStatus.UNKNOWN,
                        "unsupported_type",
                        "Overloaded candidate methods are unsupported",
                    )
                )
                findings.extend(_blocked(member, root))
                continue
            if (
                type(raw) is not types.FunctionType
                or in_instance
                or inspect.isgeneratorfunction(raw)
                or inspect.isasyncgenfunction(raw)
            ):
                findings.append(
                    _fact(
                        root,
                        EvidenceStatus.UNKNOWN,
                        "unsupported_candidate",
                        "Standard instance-method binding is required",
                    )
                )
                findings.extend(_blocked(member, root))
                continue
            kind = inspect.iscoroutinefunction(raw) == member.coroutine
            findings.append(
                _fact(
                    (member.name, "kind"),
                    EvidenceStatus.PROVEN if kind else EvidenceStatus.INCOMPATIBLE,
                    "async_mismatch",
                    "The execution kind matches"
                    if kind
                    else "The coroutine execution kind differs",
                )
            )
            signature = exposed_signature(raw, raw=ir.annotations == "raw", owner=owner)
            signature = None if signature is None else unbind(signature)
            if signature is None:
                findings.append(
                    _fact(
                        (member.name, "signature"),
                        EvidenceStatus.UNKNOWN,
                        "signature_unavailable",
                        "A standard bound signature is unavailable",
                    )
                )
                findings.extend(_blocked(member, (member.name, "signature"))[2:])
                continue
            check = check_signature(member.signature, signature)
            ctx: dict[str, object] = {}
            if check.failed_call is not None:
                ctx["call_shape"] = {
                    "positional_count": check.failed_call[0],
                    "keywords": list(check.failed_call[1]),
                }
            findings.append(
                _fact(
                    (member.name, "signature"),
                    check.shape_status,
                    "signature",
                    check.message or "Every legal required call is accepted",
                    source="signature",
                    ctx=ctx,
                )
            )
            for (name, relation), (_, got) in zip(check.parameter_relations, check.routes):
                findings.append(
                    _relation(
                        (member.name, name),
                        relation,
                        "parameter_type",
                        member.signature.parameters[name].annotation,
                        signature.parameters[got].annotation,
                        {"provided_parameter": got},
                    )
                )
                findings.extend(_uncertainties((member.name, name), relation))
            if check.return_relation is not None:
                findings.append(
                    _relation(
                        (member.name, "return"),
                        check.return_relation,
                        "return_type",
                        member.signature.return_annotation,
                        signature.return_annotation,
                    )
                )
                findings.extend(_uncertainties((member.name, "return"), check.return_relation))
        else:
            _attribute(
                member, cls, raw, owner, instance_dict, ir.annotations, findings, write_dynamic
            )
    return CompatibilityResult(ir.name, tuple(findings), len(ir.members))


def _attribute(
    member: AttributeIR,
    cls: type[object],
    raw: object,
    owner: type[object],
    instance: dict[str, object] | None,
    policy: Policy,
    findings: list[Evidence],
    write_dynamic: bool,
) -> None:
    code = "property_type" if type(raw) is property or member.property else "attribute_type"
    read_issue: Evidence | None = None
    if type(raw) is types.FunctionType and (instance is None or member.name not in instance):
        findings.append(
            _fact(
                (member.name, "kind"),
                EvidenceStatus.INCOMPATIBLE,
                "member_kind",
                "A method descriptor is not declared plain storage",
            )
        )
        findings.extend(_blocked(member, (member.name, "kind")))
        return
    if type(raw) is property:
        read: object = inspect_missing
        if raw.fget is None:
            read_issue = _fact(
                (member.name, "read"),
                EvidenceStatus.INCOMPATIBLE,
                "member_kind",
                "The readable property capability is absent",
            )
        elif type(raw.fget) is not types.FunctionType:
            read_issue = _fact(
                (member.name, "read"),
                EvidenceStatus.UNKNOWN,
                "descriptor_unverifiable",
                "A standard property getter is required",
            )
        else:
            getter = exposed_signature(raw.fget, raw=policy == "raw", owner=owner)
            getter = None if getter is None else unbind(getter)
            if (
                getter is None
                or getter.parameters
                or inspect.iscoroutinefunction(raw.fget)
                or inspect.isgeneratorfunction(raw.fget)
                or inspect.isasyncgenfunction(raw.fget)
            ):
                read_issue = _fact(
                    (member.name, "read"),
                    EvidenceStatus.UNKNOWN,
                    "signature_unavailable",
                    "A standard getter signature is unavailable",
                )
            else:
                read = getter.return_annotation
        writable = raw.fset is not None
        write: object = inspect_missing
        if raw.fset is not None:
            setter = exposed_signature(raw.fset, raw=policy == "raw", owner=owner)
            setter = None if setter is None else unbind(setter)
            if (
                setter is not None
                and len(setter.parameters) == 1
                and next(iter(setter.parameters.values())).kind
                in (inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD)
                and not inspect.iscoroutinefunction(raw.fset)
                and not inspect.isgeneratorfunction(raw.fset)
                and not inspect.isasyncgenfunction(raw.fset)
            ):
                write = next(iter(setter.parameters.values())).annotation
            else:
                write = Unavailable("signature_unavailable")
    else:
        read = inspect_missing
        for declaring in class_mro(cls):
            annotations = annotation_map(declaring, policy)
            if member.name in annotations or "__unresolved__" in annotations:
                read = declared_annotation(declaring, declaring, member.name, policy)
                break
        write = read
        writable = instance is not None and not write_dynamic
    findings.append(
        _fact(
            (member.name, "kind"),
            EvidenceStatus.PROVEN,
            "member_kind",
            "The member kind is statically established",
        )
    )
    if read_issue is not None:
        findings.append(read_issue)
    else:
        relation = relate(read, member.read_type)
        findings.append(_relation((member.name, "read"), relation, code, member.read_type, read))
        findings.extend(_uncertainties((member.name, "read"), relation))
    if member.writable:
        if write_dynamic and type(raw) is not property:
            findings.append(
                _fact(
                    (member.name, "write"),
                    EvidenceStatus.UNKNOWN,
                    "dynamic_member_unverifiable",
                    "Custom write dispatch prevents a static writable-capability proof",
                )
            )
        elif not writable:
            findings.append(
                _fact(
                    (member.name, "write"),
                    EvidenceStatus.INCOMPATIBLE,
                    "member_kind",
                    "The required writable capability is absent",
                )
            )
        else:
            relation = relate(member.write_type, write)
            findings.append(
                _relation((member.name, "write"), relation, code, member.write_type, write)
            )
            findings.extend(_uncertainties((member.name, "write"), relation))
