from __future__ import annotations

import argparse
import importlib.metadata
import json
import platform
import time
from collections.abc import Callable
from pathlib import Path
from typing import Protocol, cast

from typing_extensions import TypeForm

import stipulate
from stipulate import Contract

from .release_evidence import sha256, source_digest


class Requirement(Protocol):
    def read(self, key: str) -> bytes: ...


def wide_read(self: object, *, key: str) -> bytes:
    return b""


class Good:
    def read(self, key: object) -> bytes:
        return b""


class Bad:
    def read(self, key: int) -> bytes:
        return b""


class Unknown:
    def read(self, key: object) -> bytes:
        return b""


Unknown.read.__annotations__ = {}


def measure(workload: str, operation: Callable[[], object], iterations: int) -> dict[str, object]:
    start = time.perf_counter()
    for _ in range(iterations):
        operation()
    return {"workload": workload, "iterations": iterations, "seconds": time.perf_counter() - start}


def run(root: Path, distribution: Path, iterations: int) -> dict[str, object]:
    if "site-packages" not in Path(stipulate.__file__).parts:
        raise ValueError("Benchmark the canonical installed wheel in a clean environment")
    measurements: list[dict[str, object]] = []
    measurements.append(
        measure("cold_compile", lambda: Contract(Requirement, refresh=True), iterations)
    )
    retained = Contract(Requirement)
    measurements.append(measure("retained_construction", lambda: Contract(Requirement), iterations))
    for name, candidate in (
        ("compatible_check", Good()),
        ("incompatible_check", Bad()),
        ("unknown_check", Unknown()),
    ):
        measurements.append(measure(name, lambda: retained.check(candidate), iterations))
    good, unknown = Good(), Unknown()
    measurements.append(measure("strict_enforcement", lambda: retained.validate(good), iterations))
    measurements.append(
        measure(
            "permissive_enforcement", lambda: retained.validate(unknown, strict=False), iterations
        )
    )

    class Temporary(Protocol):
        def read(self, key: str) -> bytes: ...

    measurements.append(measure("temporary_construction", lambda: Contract(Temporary), iterations))
    wide = type(
        "Wide",
        (cast(type[object], Protocol),),
        {
            "__module__": __name__,
            "_is_protocol": True,
            **{f"method_{i:03d}": (wide_read if i == 0 else Requirement.read) for i in range(50)},
        },
    )
    wide_impl = type(
        "WideImpl",
        (),
        {f"method_{i:03d}": (wide_read if i == 0 else Good.read) for i in range(50)},
    )()
    wide_contract = Contract(cast(TypeForm[object], wide))
    measurements.append(
        measure("wide_contract", lambda: wide_contract.check(wide_impl), max(1, iterations // 20))
    )
    depth: object = int
    for _ in range(10):
        import types

        depth = types.GenericAlias(list, (depth,))

    def method(self: object) -> object:
        return None

    method.__annotations__ = {"return": depth}
    deep = type(
        "Deep",
        (cast(type[object], Protocol),),
        {"__module__": __name__, "_is_protocol": True, "read": method},
    )
    deep_impl = type("DeepImpl", (), {"read": method})()
    deep_contract = Contract(cast(TypeForm[object], deep))
    measurements.append(
        measure("deep_type", lambda: deep_contract.check(deep_impl), max(1, iterations // 20))
    )
    return {
        "release_version": importlib.metadata.version("stipulate"),
        "runtime_source_digest": source_digest(root),
        "installed_distribution_sha256": sha256(distribution),
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "machine": platform.machine(),
            "typing_extensions": importlib.metadata.version("typing_extensions"),
            "timer": "time.perf_counter",
            "aggregation": "total seconds per workload",
        },
        "tasks": (
            "Cold/retained/temporary construction; three outcomes; enforcement; "
            "50 members; ten nested invariant lists."
        ),
        "measurements": measurements,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("distribution", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--iterations", type=int, default=100)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    if args.iterations < 1:
        parser.error("iterations must be positive")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(run(args.root, args.distribution, args.iterations), indent=2) + "\n"
    )


if __name__ == "__main__":
    main()
