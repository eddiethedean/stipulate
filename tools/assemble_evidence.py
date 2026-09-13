from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import tomllib
from pathlib import Path

from .release_evidence import CRITERIA, TARGETS, read_json, record, sha256, source_digest, validate


def run(bundle: Path, root: Path, required: bool) -> None:
    version = str(tomllib.loads((root / "pyproject.toml").read_text())["project"]["version"])
    revision = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root).decode().strip()
    distributions: dict[str, object] = {}
    for kind, pattern in (("wheel", "*.whl"), ("sdist", "*.tar.gz")):
        files = list((bundle / "dist").glob(pattern))
        if len(files) != 1:
            raise ValueError("Expected exactly one canonical artifact of each kind")
        distributions[kind] = {
            "path": files[0].relative_to(bundle).as_posix(),
            "sha256": sha256(files[0]),
        }
    matrix: list[dict[str, object]] = []
    automated: list[dict[str, object]] = []
    tools: dict[str, object] = {}
    for target in sorted(TARGETS):
        quality_path = bundle / "quality" / target / "quality.json"
        quality = read_json(quality_path)
        if quality["state"] != "passed":
            raise ValueError("Source quality gate did not pass")
        if target == "3.11":
            tools = record(quality["tools"])
        for kind in ("wheel", "sdist"):
            path = bundle / "installed" / (target + "-" + kind) / "matrix.json"
            entry = read_json(path)
            if (
                entry["state"] != "passed"
                or entry["target"] != target
                or entry["distribution_sha256"] != record(distributions[kind])["sha256"]
            ):
                raise ValueError("Installed check did not use the canonical artifact")
            if kind == "wheel":
                matrix.append(entry)
        for path in [
            quality_path,
            *sorted((bundle / "quality" / target).glob("*.txt")),
            *sorted((bundle / "installed").glob(target + "-*/*.txt")),
            *sorted((bundle / "installed").glob(target + "-*/pytest.xml")),
        ]:
            automated.append(
                {
                    "kind": "automated",
                    "path": path.relative_to(bundle).as_posix(),
                    "sha256": sha256(path),
                }
            )
    inventory = read_json(root / "tools/feature_inventory.json")
    criteria: list[dict[str, object]] = []
    missing: list[str] = []
    measurements = bundle / "measurements"
    measurements.mkdir(exist_ok=True)
    for criterion in sorted(CRITERIA):
        if criterion == "AC-029":
            name = "benchmark.json"
            source = root / "docs/releases" / version / name
            if not source.is_file():
                missing.append(criterion)
                criteria.append({"id": criterion, "state": "unrun", "proofs": []})
                continue
            destination = measurements / name
            shutil.copy2(source, destination)
            proofs = [
                {
                    "kind": "benchmark",
                    "path": destination.relative_to(bundle).as_posix(),
                    "sha256": sha256(destination),
                }
            ]
        else:
            proofs = automated
        criteria.append({"id": criterion, "state": "passed", "proofs": proofs})
    evidence = {
        "format_version": 1,
        "release_version": version,
        "source_revision": revision,
        "runtime_source_digest": source_digest(root),
        "distributions": distributions,
        "tools": tools,
        "supported_features": inventory["supported"],
        "excluded_features": inventory["excluded"],
        "matrix": matrix,
        "criteria": criteria,
        "limitations": inventory["excluded"],
    }
    (bundle / "evidence.json").write_text(json.dumps(evidence, indent=2) + "\n")
    if missing:
        print("Release evidence outstanding: " + ", ".join(missing))
        if required:
            raise ValueError(
                "Release requires every active acceptance criterion, including benchmarks"
            )
        return
    validate(bundle, root, version=version, revision=revision)
    print("Complete release evidence validated.")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("bundle", type=Path)
    parser.add_argument("--required", action="store_true")
    args = parser.parse_args()
    run(args.bundle, Path.cwd(), args.required)


if __name__ == "__main__":
    main()
