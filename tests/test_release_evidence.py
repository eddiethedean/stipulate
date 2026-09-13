from __future__ import annotations

import copy
import io
import json
import tarfile
import zipfile
from pathlib import Path

import pytest

from tools import release_evidence as gate


def fixture(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> tuple[Path, Path, dict[str, object]]:
    root, bundle = tmp_path / "root", tmp_path / "bundle"
    (root / "tools").mkdir(parents=True)
    bundle.mkdir()
    inventory = Path(__file__).parents[1] / "tools/feature_inventory.json"
    (root / "tools/feature_inventory.json").write_bytes(inventory.read_bytes())
    features = gate.read_json(inventory)
    wheel = bundle / "stipulate-0.1.0-py3-none-any.whl"
    metadata = b"Name: stipulate\nVersion: 0.1.0\n"
    with zipfile.ZipFile(wheel, "w") as archive:
        archive.writestr("stipulate-0.1.0.dist-info/METADATA", metadata)
    sdist = bundle / "stipulate-0.1.0.tar.gz"
    with tarfile.open(sdist, "w:gz") as archive:
        item = tarfile.TarInfo("stipulate-0.1.0/PKG-INFO")
        item.size = len(metadata)
        archive.addfile(item, io.BytesIO(metadata))
    (bundle / "automated.txt").write_text(
        "Synthetic validator unit fixture; not release evidence.\n"
    )

    def proof(name: str, kind: str) -> dict[str, object]:
        return {"kind": kind, "path": name, "sha256": gate.sha256(bundle / name)}

    association: dict[str, object] = {
        "release_version": "0.1.0",
        "runtime_source_digest": "a" * 64,
        "installed_distribution_sha256": gate.sha256(wheel),
        "environment": "synthetic unit test",
        "tasks": "synthetic unit test",
    }
    benchmark = {
        **association,
        "measurements": [
            {"workload": n, "iterations": 1, "seconds": 0.1} for n in sorted(gate.WORKLOADS)
        ],
    }
    (bundle / "benchmark.json").write_text(json.dumps(benchmark))
    data: dict[str, object] = {
        "format_version": 1,
        "release_version": "0.1.0",
        "source_revision": "b" * 40,
        "runtime_source_digest": "a" * 64,
        "distributions": {
            "wheel": proof(wheel.name, "automated"),
            "sdist": proof(sdist.name, "automated"),
        },
        "tools": {
            "pyright": {"version": "1.1.411", "args": ["--project", "pyproject.toml"]},
            "mypy": {
                "version": "1.19.1",
                "args": ["--strict", "--enable-incomplete-feature=TypeForm"],
            },
        },
        "supported_features": features["supported"],
        "excluded_features": features["excluded"],
        "matrix": [
            {
                "target": t,
                "state": "passed",
                "python_version": t + ".1",
                "pyright_version": "1.1.411",
                "mypy_version": "1.19.1",
            }
            for t in sorted(gate.TARGETS)
        ],
        "criteria": [
            {
                "id": criterion,
                "state": "passed",
                "proofs": [
                    proof(
                        "benchmark.json" if criterion == "AC-029" else "automated.txt",
                        "benchmark" if criterion == "AC-029" else "automated",
                    )
                ],
            }
            for criterion in sorted(gate.CRITERIA)
        ],
        "limitations": features["excluded"],
    }

    def digest(root: Path) -> str:
        return "a" * 64

    monkeypatch.setattr(gate, "source_digest", digest)
    return root, bundle, data


def test_complete_associated_fixture_validates(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root, bundle, data = fixture(tmp_path, monkeypatch)
    assert "AC-030" not in gate.CRITERIA
    assert not (bundle / "usability.json").exists()
    (bundle / "evidence.json").write_text(json.dumps(data))
    gate.validate(bundle, root, version="0.1.0", revision="b" * 40)


@pytest.mark.parametrize(
    "failure",
    [
        "missing",
        "duplicate",
        "state",
        "hash",
        "escape",
        "version",
        "digest",
        "features",
        "matrix",
        "benchmark",
        "checker_flags",
    ],
)
def test_release_gate_fails_closed(
    failure: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root, bundle, initial = fixture(tmp_path, monkeypatch)
    data = copy.deepcopy(initial)
    criteria = gate.rows(data["criteria"])
    if failure == "missing":
        criteria.pop()
    elif failure == "duplicate":
        criteria.append(criteria[0])
    elif failure == "state":
        gate.record(criteria[0])["state"] = "unrun"
    elif failure in {"hash", "escape"}:
        proof = gate.record(gate.rows(gate.record(criteria[0])["proofs"])[0])
        proof["sha256" if failure == "hash" else "path"] = (
            "c" * 64 if failure == "hash" else "../outside.txt"
        )
    elif failure == "version":
        data["release_version"] = "0.1.1"
    elif failure == "digest":
        data["runtime_source_digest"] = "d" * 64
    elif failure == "features":
        gate.rows(data["supported_features"]).append("nested_protocols")
    elif failure == "matrix":
        gate.rows(data["matrix"]).pop()
    elif failure == "checker_flags":
        gate.record(gate.record(data["tools"])["mypy"])["args"] = []
    else:
        benchmark = gate.read_json(bundle / "benchmark.json")
        gate.rows(benchmark["measurements"]).pop()
        (bundle / "benchmark.json").write_text(json.dumps(benchmark))
        row = next(gate.record(r) for r in criteria if gate.record(r)["id"] == "AC-029")
        gate.record(gate.rows(row["proofs"])[0])["sha256"] = gate.sha256(bundle / "benchmark.json")
    (bundle / "evidence.json").write_text(json.dumps(data))
    with pytest.raises(ValueError):
        gate.validate(bundle, root, version="0.1.0", revision="b" * 40)


def test_duplicate_json_keys_are_rejected(tmp_path: Path) -> None:
    path = tmp_path / "duplicate.json"
    path.write_text('{"format_version": 1, "format_version": 1}')
    with pytest.raises(ValueError, match="Duplicate"):
        gate.read_json(path)


def test_embedded_metadata_mismatch_is_detected(tmp_path: Path) -> None:
    path = tmp_path / "stipulate-0.1.0-py3-none-any.whl"
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("stipulate-0.1.0.dist-info/METADATA", "Name: stipulate\nVersion: 9.9.9\n")
    assert gate.embedded_version(path) == "9.9.9"
