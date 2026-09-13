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
5. The build job creates one wheel and one source distribution, verifies both versions against the tag, and runs `twine check`.
6. The publish job downloads only those checked artifacts and publishes through OIDC trusted publishing.

The release workflow accepts the broad trigger pattern `v*.*.*` so future release lines can use the same file, but the reusable check currently permits only the `0.1` phase. Promote the allowed phase deliberately when the roadmap and release gates move forward.

## Recovery and safety

- Re-running the same tag is safe only if PyPI has not already accepted that version; PyPI versions are immutable.
- If checks fail, fix the source and create a new patch tag. Do not force-move a release tag.
- If the environment approval is pending, review the completed check and build jobs before approving publish.
- If trusted publishing fails, check the PyPI publisher fields and the GitHub environment name before changing workflow permissions.
- The workflow has no long-lived PyPI credential to rotate or revoke.

## Local preflight

Before pushing a release tag, run the checks listed in [design_probes/README.md](../design_probes/README.md), the package test suite when `pyproject.toml` exists, and:

```sh
python -m build --sdist --wheel
python -m twine check dist/*
```

The current checkout is design-stage and does not yet contain `pyproject.toml`; therefore a release tag will intentionally stop at the build metadata check until the package foundation is implemented.
