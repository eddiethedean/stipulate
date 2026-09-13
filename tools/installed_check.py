from __future__ import annotations

import argparse
import json
import os
import platform
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from .release_evidence import record, sha256


def command(
    argv: list[str],
    cwd: Path,
    env: dict[str, str],
    *,
    succeeds: bool = True,
    stdout_only: bool = False,
) -> str:
    completed = subprocess.run(argv, cwd=cwd, env=env, capture_output=True, text=True)
    if (completed.returncode == 0) != succeeds:
        raise RuntimeError(
            "Verification failed: " + " ".join(argv) + "\n" + completed.stdout + completed.stderr
        )
    return completed.stdout if stdout_only else completed.stdout + completed.stderr


def run(distribution: Path, output: Path, root: Path) -> None:
    distribution = distribution.resolve()
    root = root.resolve()
    env = dict(os.environ)
    env.pop("PYTHONPATH", None)
    env["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"
    env["PYRIGHT_PYTHON_FORCE_VERSION"] = "1.1.411"
    with tempfile.TemporaryDirectory(prefix="stipulate-installed-") as temporary:
        work = Path(temporary)
        venv = work / "venv"
        command(["uv", "venv", "--python", sys.executable, str(venv)], work, env)
        python = str(venv / "bin/python")
        requirements = work / "development.txt"
        exported = command(
            ["uv", "export", "--locked", "--extra", "dev", "--no-emit-project"],
            root,
            env,
            stdout_only=True,
        )
        requirements.write_text(exported)
        command(["uv", "pip", "install", "--python", python, "-r", str(requirements)], work, env)
        command(
            [
                "uv",
                "pip",
                "install",
                "--python",
                python,
                str(distribution),
                "typing_extensions==4.15.0",
            ],
            work,
            env,
        )
        for folder in ("tests", "docs", "tools", "design_probes"):
            shutil.copytree(
                root / folder, work / folder, ignore=shutil.ignore_patterns("__pycache__")
            )
        shutil.copy2(root / "README.md", work / "README.md")
        # Tests and checkers run outside the repository; there is no copied src
        # tree or editable install to conceal a missing wheel member or py.typed.
        logs: dict[str, str] = {}
        logs["origin"] = command(
            [
                python,
                "-c",
                "import stipulate; from pathlib import Path; p=Path(stipulate.__file__); "
                "assert 'site-packages' in str(p); "
                "assert p.with_name('py.typed').is_file(); print(p)",
            ],
            work,
            env,
        )
        logs["pytest"] = command(
            [python, "-m", "pytest", "-q", "--junitxml=pytest.xml", "tests"], work, env
        )
        config = work / "pyrightconfig.json"
        config.write_text(
            json.dumps(
                {
                    "include": ["tests/typing_fixtures/public_api.py"],
                    "typeCheckingMode": "strict",
                    "pythonVersion": ".".join(platform.python_version_tuple()[:2]),
                }
            )
        )
        pyright = str(venv / "bin/pyright")
        pyright_args = [pyright, "--project", str(config), "--pythonpath", python]
        logs["pyright_positive"] = command(pyright_args, work, env)
        logs["pyright_negative"] = command(
            [
                *pyright_args,
                "tests/typing_fixtures/negative.py",
                "--outputjson",
            ],
            work,
            env,
            succeeds=False,
            stdout_only=True,
        )
        negative = json.loads(logs["pyright_negative"].split("WARNING:", 1)[0])
        diagnostics = [d for d in negative["generalDiagnostics"] if d["severity"] == "error"]
        if [d["rule"] for d in diagnostics] != [
            "reportAssignmentType",
            "reportAssignmentType",
            "reportArgumentType",
            "reportCallIssue",
            "reportCallIssue",
        ]:
            raise ValueError("Unexpected installed negative Pyright diagnostics")
        mypy = [
            str(venv / "bin/mypy"),
            "--strict",
            "--enable-incomplete-feature=TypeForm",
            "--no-incremental",
            "--python-executable",
            python,
        ]
        logs["mypy_positive"] = command([*mypy, "tests/typing_fixtures/public_api.py"], work, env)
        logs["mypy_negative"] = command(
            [*mypy, "tests/typing_fixtures/negative.py"], work, env, succeeds=False
        )
        if logs["mypy_negative"].count(": error:") != 5:
            raise ValueError("Unexpected installed negative mypy diagnostics")
        versions = record(
            json.loads(
                command(
                    [
                        python,
                        "-c",
                        "import importlib.metadata as m, json; "
                        "print(json.dumps({n: m.version(n) for n in "
                        "('pyright', 'mypy', 'typing_extensions')}))",
                    ],
                    work,
                    env,
                )
            )
        )
        output.mkdir(parents=True, exist_ok=True)
        shutil.copy2(work / "pytest.xml", output / "pytest.xml")
        for name, log in logs.items():
            (output / (name + ".txt")).write_text(log)
        (output / "matrix.json").write_text(
            json.dumps(
                {
                    "target": ".".join(platform.python_version_tuple()[:2]),
                    "python_version": platform.python_version(),
                    "state": "passed",
                    "distribution_sha256": sha256(distribution),
                    "pyright_version": versions["pyright"],
                    "mypy_version": versions["mypy"],
                    "typing_extensions_version": versions["typing_extensions"],
                    "distribution": distribution.name,
                },
                indent=2,
            )
            + "\n"
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("distribution", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    run(args.distribution, args.output, Path.cwd())


if __name__ == "__main__":
    main()
