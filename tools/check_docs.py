from __future__ import annotations

import re
from pathlib import Path


def main() -> None:
    paths = [Path("README.md"), *Path("docs").rglob("*.md"), Path("design_probes/README.md")]
    errors: list[str] = []
    for path in paths:
        text = path.read_text()
        if text.count("```") % 2:
            errors.append(f"{path}: unmatched code fence")
        if any(line != line.rstrip() for line in text.splitlines()):
            errors.append(f"{path}: trailing whitespace")
        prose = re.sub(r"```[^\n]*\n.*?```", "", text, flags=re.S)
        prose = re.sub(r"`[^`\n]*`", "", prose)
        for target in re.findall(r"(?<!!)\[[^\]]*\]\(([^)]+)\)", prose):
            target = target.split("#", 1)[0]
            if target and "://" not in target and not (path.parent / target).exists():
                errors.append(f"{path}: missing {target}")
    if errors:
        raise SystemExit("\n".join(errors))
    print(f"Checked {len(paths)} Markdown files.")


if __name__ == "__main__":
    main()
