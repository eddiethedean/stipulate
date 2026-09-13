# Releasing Stipulate

This repository's release workflow is prepared for the first `0.1` release. It is deliberately tag-driven and fail-closed: a release cannot publish until the reusable checks pass, the tag is a semantic `v0.1.X` tag, and the wheel and source distribution contain the same version.

## One-time trusted-publisher setup

Create a PyPI trusted publisher for:

| Field | Value |
| --- | --- |
| Owner | `eddiethedean` |
| Repository | `stipulate` |
| Workflow | `release.yml` |
| Environment | `pypi` |

Create a GitHub environment named `pypi`. Add required reviewers there if releases should require an approval after checks and before the OIDC publish step. Do not add a `PYPI_API_TOKEN` secret; trusted publishing exchanges the job's short-lived GitHub OIDC identity for a PyPI upload token.

The PyPI project must exist or be created through its trusted-publisher flow before the first upload. The workflow's publisher identity includes the repository, workflow filename, and environment, so renaming any of them requires updating the PyPI publisher configuration too.

## Release flow

1. Complete the `0.1` release gates in [ROADMAP.md](ROADMAP.md) and [OPEN_TECHNICAL_PROBLEMS.md](OPEN_TECHNICAL_PROBLEMS.md).
2. Set the package version in `pyproject.toml` to the exact patch version being released.
3. Push an annotated tag matching `v0.1.X`, for example `v0.1.0`.
4. `release.yml` calls [check.yml](../.github/workflows/check.yml) as a reusable workflow and waits for it to pass.
5. The reusable checks run source quality on 3.11–3.14, build canonical distributions once on 3.11, then test both artifacts in isolated installed consumers on every target, including both checkers and negative fixtures.
6. The evidence job associates those exact artifacts with all 30 active acceptance criteria (AC-030 was withdrawn by the user). A release call fails if benchmark evidence is absent, incomplete, stale, or associated with different source/artifact hashes.
7. Release verification downloads the checked bundle, verifies tag, source digest, artifact hashes and embedded wheel METADATA/sdist PKG-INFO without rebuilding. Publish downloads only that verified distribution set and uses OIDC.

The release workflow accepts the broad trigger pattern `v*.*.*` so future release lines can use the same file, but the reusable check currently permits only the `0.1` phase. Promote the allowed phase deliberately when the roadmap and release gates move forward.

## Recovery and safety

- Re-running the same tag is safe only if PyPI has not already accepted that version; PyPI versions are immutable.
- If checks fail, fix the source and create a new patch tag. Do not force-move a release tag.
- If the environment approval is pending, review the completed check and build jobs before approving publish.
- If trusted publishing fails, check the PyPI publisher fields and the GitHub environment name before changing workflow permissions.
- The workflow has no long-lived PyPI credential to rotate or revoke.

## Local preflight

Before pushing a release tag, install the locked development environment and run:

```sh
uv sync --locked --extra dev --python 3.11
uv run --locked --extra dev python -m tools.quality
SOURCE_DATE_EPOCH=315532800 uv run --locked --extra dev python -m build --sdist --wheel
uv run --locked --extra dev twine check dist/*
uv run --locked --extra dev python -m tools.installed_check dist/stipulate-0.1.0-py3-none-any.whl --output evidence/installed/3.11-wheel
uv run --locked --extra dev python -m tools.installed_check dist/stipulate-0.1.0.tar.gz --output evidence/installed/3.11-sdist
```

Repeat installed consumers on all targets. CI performs these commands against one canonical distribution set. SOURCE_DATE_EPOCH fixes wheel timestamps so the same source/backend produces the same wheel bytes across observation/evidence commits; sdist hashes still belong to the exact canonical build.

## Evidence inputs and validation

Store measured benchmark inputs under docs/releases/0.1.0/. Participant research is optional and is not a release gate. Run `python -m tools.benchmark` from an environment with the canonical wheel installed, supplying its path, --root pointing to the tracked checkout, and --output pointing to docs/releases/0.1.0/benchmark.json. The CLI records version, source digest, installed artifact hash, environment and all ten required workloads without a latency threshold.

Source digests hash sorted tracked runtime sources, pyproject.toml, MANIFEST.in, uv.lock, feature inventory, workflow configuration, README and docs except docs/releases/. Each entry is path, NUL, content SHA-256, newline; the entire sequence is then SHA-256 hashed. Track final files before measuring. Any runtime/instructional/configuration change requires matching fresh evidence; evidence-only commits do not change the digest.

`python -m tools.assemble_evidence evidence` assembles ordinary automated CI artifacts and reports missing benchmark inputs. `--required` requires every active criterion. `python -m tools.release_evidence evidence --version 0.1.0 --revision <checked-out-SHA>` rejects missing/duplicate/unrun rows, unsafe paths, missing or changed proofs, stale source, unsupported feature claims, missing matrix targets, incorrect checker settings, incomplete benchmark workloads.

Independent Sol Production Code Review remains outstanding. AC-030 has been withdrawn at the user’s request. Implementation and successful automated checks do not constitute release approval.
