from __future__ import annotations

import argparse
import email.parser
import hashlib
import json
import re
import subprocess
import tarfile
import zipfile
from pathlib import Path
from typing import cast

TARGETS = {"3.11", "3.12", "3.13", "3.14"}
CRITERIA = {f"AC-{i:03d}" for i in range(1, 32) if i != 30}
WORKLOADS = {
    "cold_compile",
    "retained_construction",
    "temporary_construction",
    "compatible_check",
    "incompatible_check",
    "unknown_check",
    "strict_enforcement",
    "permissive_enforcement",
    "wide_contract",
    "deep_type",
}


def record(value: object) -> dict[str, object]:
    if not isinstance(value, dict):
        raise ValueError("Expected an object")
    return cast(dict[str, object], value)


def rows(value: object) -> list[object]:
    if not isinstance(value, list):
        raise ValueError("Expected an array")
    return cast(list[object], value)


def string(value: object) -> str:
    if not isinstance(value, str):
        raise ValueError("Expected a string")
    return value


def read_json(path: Path) -> dict[str, object]:
    def unique(pairs: list[tuple[str, object]]) -> dict[str, object]:
        result: dict[str, object] = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("Duplicate JSON key")
            result[key] = value
        return result

    return record(json.loads(path.read_text(), object_pairs_hook=unique))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_digest(root: Path) -> str:
    tracked = subprocess.check_output(["git", "ls-files", "-z"], cwd=root).decode().split("\0")
    selected = sorted(
        p
        for p in tracked
        if p
        and (
            p.startswith("src/stipulate/")
            or p
            in {
                "pyproject.toml",
                "MANIFEST.in",
                "uv.lock",
                "README.md",
                "tools/feature_inventory.json",
            }
            or p.startswith(".github/workflows/")
            or (p.startswith("docs/") and not p.startswith("docs/releases/"))
        )
    )
    if not any(p.startswith("src/stipulate/") for p in selected):
        raise ValueError("Runtime sources must be tracked before computing evidence")
    payload = "".join(p + "\0" + sha256(root / p) + "\n" for p in selected)
    return hashlib.sha256(payload.encode()).hexdigest()


def artifact(root: Path, proof: dict[str, object]) -> Path:
    relative = Path(string(proof["path"]))
    resolved = (root / relative).resolve()
    if (
        relative.is_absolute()
        or not resolved.is_relative_to(root.resolve())
        or not resolved.is_file()
    ):
        raise ValueError("Artifact path escapes the bundle or is missing")
    if sha256(resolved) != proof["sha256"]:
        raise ValueError("Artifact hash mismatch")
    return resolved


def embedded_version(path: Path) -> str:
    if path.suffix == ".whl":
        with zipfile.ZipFile(path) as archive:
            names = [n for n in archive.namelist() if n.endswith(".dist-info/METADATA")]
            if len(names) != 1:
                raise ValueError("Expected one wheel METADATA")
            data = archive.read(names[0])
    else:
        with tarfile.open(path, "r:gz") as archive:
            members = [
                m
                for m in archive.getmembers()
                if m.name.count("/") == 1 and m.name.endswith("/PKG-INFO")
            ]
            if len(members) != 1 or not members[0].isfile():
                raise ValueError("Expected one sdist PKG-INFO")
            stream = archive.extractfile(members[0])
            if stream is None:
                raise ValueError("Missing PKG-INFO contents")
            data = stream.read()
    metadata = email.parser.BytesParser().parsebytes(data)
    if metadata.get("Name") != "stipulate":
        raise ValueError("Unexpected distribution name")
    return string(metadata.get("Version"))


def validate_benchmark(path: Path, evidence: dict[str, object]) -> None:
    data = read_json(path)
    hashes = {record(v)["sha256"] for v in record(evidence["distributions"]).values()}
    if (
        data.get("release_version") != evidence["release_version"]
        or data.get("runtime_source_digest") != evidence["runtime_source_digest"]
        or data.get("installed_distribution_sha256") not in hashes
    ):
        raise ValueError("Benchmark evidence belongs to a different candidate")
    if not data.get("environment") or not data.get("tasks"):
        raise ValueError("Benchmark evidence lacks environment/tasks")
    measurements = rows(data["measurements"])
    names = [record(m)["workload"] for m in measurements]
    if len(names) != len(set(names)) or set(names) != WORKLOADS:
        raise ValueError("Benchmark workloads are incomplete")
    for measurement in measurements:
        m = record(measurement)
        if (
            type(m.get("iterations")) is not int
            or cast(int, m["iterations"]) < 1
            or type(m.get("seconds")) not in (int, float)
            or not 0 <= cast(float, m["seconds"]) < float("inf")
        ):
            raise ValueError("Invalid benchmark measurement")


def validate(bundle: Path, root: Path, *, version: str, revision: str) -> None:
    evidence = read_json(bundle / "evidence.json")
    required = {
        "format_version",
        "release_version",
        "source_revision",
        "runtime_source_digest",
        "distributions",
        "tools",
        "supported_features",
        "excluded_features",
        "matrix",
        "criteria",
        "limitations",
    }
    if (
        set(evidence) != required
        or type(evidence["format_version"]) is not int
        or evidence["format_version"] != 1
    ):
        raise ValueError("Invalid evidence schema")
    if re.fullmatch(r"0\.1\.[0-9]+", version) is None or evidence["release_version"] != version:
        raise ValueError("Release version mismatch")
    if re.fullmatch(r"[0-9a-f]{40}", revision) is None or evidence["source_revision"] != revision:
        raise ValueError("Source revision mismatch")
    if evidence["runtime_source_digest"] != source_digest(root):
        raise ValueError("Runtime source digest mismatch")
    inventory = read_json(root / "tools/feature_inventory.json")
    for field, source in (("supported_features", "supported"), ("excluded_features", "excluded")):
        if evidence[field] != inventory[source]:
            raise ValueError("Claimed feature inventory differs from the approved boundary")
    if not all(
        string(item) in rows(inventory["excluded"]) for item in rows(evidence["limitations"])
    ):
        raise ValueError("Undocumented limitation")
    distributions = record(evidence["distributions"])
    if set(distributions) != {"wheel", "sdist"}:
        raise ValueError("Expected wheel and sdist")
    for kind, value in distributions.items():
        path = artifact(bundle, record(value))
        if (
            not path.name.endswith(".whl" if kind == "wheel" else ".tar.gz")
            or embedded_version(path) != version
        ):
            raise ValueError("Embedded distribution version/type mismatch")
    tools = record(evidence["tools"])
    for tool, expected in (("pyright", "1.1.411"), ("mypy", "1.19.1")):
        entry = record(tools[tool])
        if entry["version"] != expected or not all(isinstance(a, str) for a in rows(entry["args"])):
            raise ValueError("Missing pinned checker/arguments")
    if "--strict" not in rows(
        record(tools["mypy"])["args"]
    ) or "--enable-incomplete-feature=TypeForm" not in rows(record(tools["mypy"])["args"]):
        raise ValueError("Missing mypy consumer settings")
    matrix = rows(evidence["matrix"])
    targets: list[str] = []
    for item in matrix:
        entry = record(item)
        target = string(entry["target"])
        targets.append(target)
        if (
            entry["state"] != "passed"
            or not string(entry["python_version"]).startswith(target + ".")
            or entry.get("pyright_version") != "1.1.411"
            or entry.get("mypy_version") != "1.19.1"
        ):
            raise ValueError("Incomplete runtime/checker matrix")
    if len(targets) != 4 or set(targets) != TARGETS:
        raise ValueError("Missing or duplicate runtime target")
    criteria = rows(evidence["criteria"])
    ids: list[str] = []
    for item in criteria:
        entry = record(item)
        criterion = string(entry["id"])
        ids.append(criterion)
        proofs = rows(entry["proofs"])
        if entry["state"] != "passed" or not proofs:
            raise ValueError("Unproven acceptance criterion")
        has_required_kind = False
        for value in proofs:
            proof = record(value)
            if proof["kind"] not in {"automated", "manual", "benchmark"}:
                raise ValueError("Unknown proof kind")
            path = artifact(bundle, proof)
            if criterion == "AC-029" and proof["kind"] == "benchmark":
                validate_benchmark(path, evidence)
                has_required_kind = True
        if criterion == "AC-029" and not has_required_kind:
            raise ValueError("Missing benchmark evidence")
    if len(ids) != len(CRITERIA) or set(ids) != CRITERIA:
        raise ValueError("Missing or duplicate acceptance criterion")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("bundle", type=Path)
    parser.add_argument("--version", required=True)
    parser.add_argument("--revision", required=True)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    validate(args.bundle, args.root, version=args.version, revision=args.revision)
    print("Complete release evidence verified against source and exact distributions.")


if __name__ == "__main__":
    main()
