from __future__ import annotations

import textwrap
import unicodedata

from ._evidence import Evidence, EvidenceStatus


def safe(text: str) -> str:
    return "".join(
        f"\\u{ord(c):04x}" if unicodedata.category(c).startswith("C") else c for c in text
    )


def wrapped(text: str, indent: str = "") -> list[str]:
    return textwrap.wrap(safe(text), width=60, initial_indent=indent, subsequent_indent=indent) or [
        indent
    ]


def render_result(name: str, status: str, evidence: tuple[Evidence, ...], members: int) -> str:
    headline = {
        "compatible": "Compatible with",
        "incompatible": "Incompatible with",
        "unknown": "Compatibility unknown for",
    }[status]
    lines = wrapped(f"{headline} {name}")
    if status == "compatible":
        lines.extend(
            wrapped(
                "No required members. No capabilities were established."
                if not members
                else "All required declarations are compatible."
            )
        )
        return "\n".join(lines)
    errors = sum(e.status is EvidenceStatus.INCOMPATIBLE for e in evidence)
    unknowns = sum(e.status is EvidenceStatus.UNKNOWN for e in evidence)
    blocked = sum(e.code == "dependency_unassessed" for e in evidence)
    lines.extend(
        wrapped(
            f"{errors} incompatible findings; {unknowns} unknown findings "
            f"({blocked} blocked obligations)."
        )
    )
    for item in evidence:
        if item.status is EvidenceStatus.PROVEN or item.code == "dependency_unassessed":
            continue
        lines.append("")
        lines.extend(wrapped(".".join(str(p) for p in item.loc) or "<contract>"))
        lines.extend(wrapped(item.msg, "  "))
        for label, value in (("Required", item.expected), ("Provided", item.actual)):
            if value is not None:
                lines.extend(wrapped(f"{label}: {value}", "  "))
        if item.hint:
            lines.extend(wrapped(item.hint, "  "))
        lines.extend(wrapped(f"[{item.code}; {item.status.value}]", "  "))
    if blocked:
        lines.extend(
            wrapped(
                f"{blocked} dependent obligations remain unassessed; see structured unknowns()."
            )
        )
    return "\n".join(lines)
