from __future__ import annotations

import importlib.metadata
import json
import os
import platform
import sys
from pathlib import Path

from .installed_check import command


def main() -> None:
    root = Path.cwd()
    output = root / "evidence/quality" / ".".join(platform.python_version_tuple()[:2])
    output.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ)
    env["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"
    env["PYRIGHT_PYTHON_FORCE_VERSION"] = "1.1.411"
    commands: dict[str, list[str]] = {
        "pytest": [sys.executable, "-m", "pytest", "-q", f"--junitxml={output / 'pytest.xml'}"],
        "ruff": ["ruff", "check", "src", "tests", "tools"],
        "format": ["ruff", "format", "--check", "src", "tests", "tools"],
        "pyright": ["pyright"],
        "mypy": [
            "mypy",
            "--strict",
            "--enable-incomplete-feature=TypeForm",
            "--no-incremental",
            "src",
            "tests/typing_fixtures/public_api.py",
        ],
        "probe_pyright": ["pyright", "--project", "design_probes/pyrightconfig.json"],
        "probe_runtime": [sys.executable, "design_probes/runtime_assumptions.py"],
        "probe_mypy": [
            "mypy",
            "--strict",
            "--enable-incomplete-feature=TypeForm",
            "--no-incremental",
            "design_probes/positive.py",
            "design_probes/runtime_assumptions.py",
        ],
        "docs": [sys.executable, "-m", "tools.check_docs"],
    }
    for name, argv in commands.items():
        (output / (name + ".txt")).write_text(command(argv, root, env))
        print(name + " passed", flush=True)
    negative = command(
        [
            "pyright",
            "--project",
            "design_probes/pyrightconfig.json",
            "design_probes/negative.py",
            "--outputjson",
        ],
        root,
        env,
        succeeds=False,
        stdout_only=True,
    )
    data = json.loads(negative.split("WARNING:", 1)[0])
    rules = [d["rule"] for d in data["generalDiagnostics"] if d["severity"] == "error"]
    if rules != [
        "reportAssignmentType",
        "reportAssignmentType",
        "reportArgumentType",
        "reportAssignmentType",
        "reportArgumentType",
    ]:
        raise ValueError("Design negative Pyright regression")
    (output / "probe_pyright_negative.txt").write_text(negative)
    negative_mypy = command(
        [
            "mypy",
            "--strict",
            "--enable-incomplete-feature=TypeForm",
            "--no-incremental",
            "design_probes/negative.py",
            "design_probes/legacy_type_parameter.py",
        ],
        root,
        env,
        succeeds=False,
    )
    if (
        negative_mypy.count(": error:") != 6
        or "[type-abstract]" not in negative_mypy
        or "[arg-type]" not in negative_mypy
    ):
        raise ValueError("Design negative mypy regression")
    (output / "probe_mypy_negative.txt").write_text(negative_mypy)
    tools = {
        name: {"version": importlib.metadata.version(name), "args": argv[1:]}
        for name, argv in commands.items()
        if name in {"pytest", "ruff", "pyright", "mypy"}
    }
    (output / "quality.json").write_text(
        json.dumps(
            {"state": "passed", "python_version": platform.python_version(), "tools": tools},
            indent=2,
        )
        + "\n"
    )


if __name__ == "__main__":
    main()
