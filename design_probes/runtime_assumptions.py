"""Check Python behaviors behind the plan; this does not implement Stipulate."""

import gc
import weakref
from dataclasses import dataclass
from typing import get_type_hints


@dataclass(frozen=True, slots=True, weakref_slot=True)
class Snapshot:
    declaration: type[object]


def populate_strong_value_cache(
    cache: weakref.WeakKeyDictionary[type[object], Snapshot],
) -> weakref.ReferenceType[type[object]]:
    class TemporaryDeclaration:
        pass

    cache[TemporaryDeclaration] = Snapshot(TemporaryDeclaration)
    return weakref.ref(TemporaryDeclaration)


def populate_weak_value_cache(
    cache: weakref.WeakKeyDictionary[
        type[object], weakref.ReferenceType[Snapshot]
    ],
) -> tuple[Snapshot, weakref.ReferenceType[type[object]]]:
    class TemporaryDeclaration:
        pass

    snapshot = Snapshot(TemporaryDeclaration)
    cache[TemporaryDeclaration] = weakref.ref(snapshot)
    return snapshot, weakref.ref(TemporaryDeclaration)


def check_cache_ownership() -> None:
    strong_values: weakref.WeakKeyDictionary[type[object], Snapshot] = (
        weakref.WeakKeyDictionary()
    )
    retained = populate_strong_value_cache(strong_values)
    gc.collect()
    assert retained() is not None, "Strong values retain their own weak keys"
    strong_values.clear()
    gc.collect()
    assert retained() is None

    weak_values: weakref.WeakKeyDictionary[
        type[object], weakref.ReferenceType[Snapshot]
    ] = weakref.WeakKeyDictionary()
    owner, released = populate_weak_value_cache(weak_values)
    gc.collect()
    assert released() is not None, "A retained snapshot intentionally owns its type"
    del owner
    gc.collect()
    assert released() is None, "The global weak cache must not retain a dead type"
    assert not weak_values


def check_annotation_evaluation() -> None:
    effects: list[str] = []

    def annotation_factory() -> type[int]:
        effects.append("evaluated")
        return int

    def candidate(value: object) -> None:
        pass

    # Runtime fixture construction: avoid an invalid static annotation expression.
    candidate.__annotations__ = {"value": "annotation_factory()", "return": None}
    assert not effects
    get_type_hints(candidate, localns={"annotation_factory": annotation_factory})
    assert effects == ["evaluated"]


if __name__ == "__main__":
    check_cache_ownership()
    check_annotation_evaluation()
    print("Python cache-ownership and annotation-evaluation probes passed.")
