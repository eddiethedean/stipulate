from __future__ import annotations

import inspect
import itertools
from typing import Callable, cast

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from stipulate._evidence import EvidenceStatus as S
from stipulate._signatures import check_signature

P = inspect.Parameter


def signature(text: str) -> inspect.Signature:
    namespace: dict[str, object] = {}
    exec("def f(" + text + ") -> int: pass", namespace)
    return inspect.signature(cast(Callable[..., object], namespace["f"]))


@pytest.mark.parametrize(
    ("required", "provided", "passes"),
    [
        ("x:int", "*args:int, **kwargs:int", True),
        ("x:int, /", "y:int", True),
        ("x:int", "x:int, /", False),
        ("x:int=1", "x:int", False),
        ("*args:int", "x:int, *args:int", False),
        ("**kwargs:int", "*, x:int, **kwargs:int", False),
        ("x:int, /, **kwargs:int", "x:int, **kwargs:int", False),
        ("x:int, /, **kwargs:int", "*args:int, **kwargs:int", True),
        ("x:int, *, y:int=0", "x:int, **kwargs:int", True),
        ("*args:int, **kwargs:int", "*args:int, **kwargs:int", True),
    ],
)
def test_call_shape_regressions(required: str, provided: str, passes: bool) -> None:
    result = check_signature(signature(required), signature(provided))
    assert (result.shape_status is S.PROVEN) == passes


@st.composite
def signatures(draw: st.DrawFn) -> inspect.Signature:
    positional = draw(st.integers(0, 3))
    only = draw(st.integers(0, positional))
    optional = draw(st.integers(0, positional))
    params = [
        P(
            "p" + str(i),
            P.POSITIONAL_ONLY if i < only else P.POSITIONAL_OR_KEYWORD,
            annotation=int,
            default=0 if i >= positional - optional else P.empty,
        )
        for i in range(positional)
    ]
    if draw(st.booleans()):
        params.append(P("args", P.VAR_POSITIONAL, annotation=int))
    for i in range(draw(st.integers(0, 2))):
        params.append(
            P(
                "k" + str(i),
                P.KEYWORD_ONLY,
                annotation=int,
                default=0 if draw(st.booleans()) else P.empty,
            )
        )
    if draw(st.booleans()):
        params.append(P("kwargs", P.VAR_KEYWORD, annotation=int))
    return inspect.Signature(params, return_annotation=int)


@given(signatures(), signatures())
@settings(max_examples=100, deadline=None)
def test_partition_matches_independent_python_call_oracle(
    required: inspect.Signature,
    provided: inspect.Signature,
) -> None:
    # Execute generated inert functions (never the candidate). Python's actual
    # call binder is independent of inspect.Signature.bind used by the engine.
    def function(sig: inspect.Signature) -> Callable[..., object]:
        namespace: dict[str, object] = {}
        exec("def f" + str(sig) + ": return None", namespace)
        return cast(Callable[..., object], namespace["f"])

    req, got = function(required), function(provided)
    names = sorted(set(required.parameters) | set(provided.parameters) | {"fresh", "other"})
    rejected = False
    for count in range(6):
        for flags in itertools.product((False, True), repeat=len(names)):
            keywords = {n: 1 for n, enabled in zip(names, flags) if enabled}
            args = (1,) * count
            try:
                req(*args, **keywords)
            except TypeError:
                continue
            try:
                got(*args, **keywords)
            except TypeError:
                rejected = True
    assert (check_signature(required, provided).shape_status is S.INCOMPATIBLE) == rejected
