# nuv

[![PyPI version](https://img.shields.io/pypi/v/nuv?logo=pypi&logoColor=white)](https://pypi.org/project/nuv/)
[![Python versions](https://img.shields.io/pypi/pyversions/nuv?logo=python&logoColor=white)](https://pypi.org/project/nuv/)
[![License](https://img.shields.io/pypi/l/nuv)](https://github.com/stevencarpenter/nuv/blob/main/LICENSE)
[![PyPI monthly downloads](https://img.shields.io/pypi/dm/nuv?logo=pypi&logoColor=white)](https://pypi.org/project/nuv/)
[![Downloads](https://static.pepy.tech/badge/nuv)](https://pepy.tech/project/nuv)
[![Wheel](https://img.shields.io/pypi/wheel/nuv)](https://pypi.org/project/nuv/#files)
[![CI](https://img.shields.io/github/actions/workflow/status/stevencarpenter/nuv/ci.yml?branch=main&label=CI)](https://github.com/stevencarpenter/nuv/actions/workflows/ci.yml)
[![Publish to PyPI](https://img.shields.io/github/actions/workflow/status/stevencarpenter/nuv/publish-pypi.yml?label=publish)](https://github.com/stevencarpenter/nuv/actions/workflows/publish-pypi.yml)
[![Coverage](https://img.shields.io/badge/coverage-100%25-brightgreen)](https://github.com/stevencarpenter/nuv/actions/workflows/ci.yml)
[![Lint: Ruff](https://img.shields.io/badge/lint-ruff-46A2F1?logo=ruff&logoColor=white)](https://docs.astral.sh/ruff/)
[![Types: ty](https://img.shields.io/badge/types-ty-0F766E)](https://github.com/astral-sh/ty)

Scaffold opinionated uv Python projects — tests passing, quality tooling green, out of the box.

Links: [PyPI](https://pypi.org/project/nuv/) | [Repository](https://github.com/stevencarpenter/nuv) | [Issues](https://github.com/stevencarpenter/nuv/issues)

```
nuv new my-tool
```

That's it. You get a working project with argparse, logging, 100% test coverage, ruff, and ty all green from commit zero.

## Install

```bash
uv tool install nuv
```

## Run without installing

```bash
uvx nuv new my-tool
```

## Usage

```
nuv new <name>                              # creates ./<name>/, syncs deps, prints tool install command
nuv new <name> --at <path>                  # creates at an explicit path
nuv new <name> --install none               # scaffold + sync, skip tool install
nuv new <name> --install command-only       # log install command, do not execute
nuv new <name> --keep-on-failure            # keep generated files if sync/install fails
```

### What you get

```
my-tool/
├── main.py          # argparse + logging + PROJECT_NAME constant
├── pyproject.toml   # pytest (100% cov), ruff, ty, uv dev deps
├── README.md
└── tests/
    ├── __init__.py
    └── test_main.py  # passing test from day one
```

By default, `nuv new` logs the command you can run to install the generated project as a tool:

```bash
uv tool install --editable <project-path>
```

After `nuv new`, all of these pass immediately:

```bash
uv run pytest       # 1 test, 100% coverage
uv run ruff check . # clean
uv run ty check     # clean
```

## Project quality

| Tool | Config |
|---|---|
| pytest | 100% branch coverage enforced |
| ruff | lint + format |
| ty | type checking |

## Why

`uv init` produces a stub. The gap between that and "actually writing code" is annoying when you create projects frequently. `nuv` closes it.

## Future archetypes

The `--archetype` flag is reserved for upcoming project types:

```bash
nuv new my-api --archetype fastapi   # coming soon
nuv new my-job --archetype spark     # coming soon
```

## Two-layer installation roadmap

We are evolving `nuv` toward two explicit layers:

1. **Install `nuv` anywhere** via `uv tool install` (or run without install using `uvx`).
2. **Install generated projects** explicitly when you want a tool install (`nuv new` now defaults to command-only guidance).

See the design brainstorm and phased proposal in `docs/plans/2026-02-26-two-layer-installation.md`.


## Publishing to PyPI

This project is configured for trusted publishing from GitHub Actions.

1. Create a [PyPI project](https://pypi.org/manage/projects/) named `nuv` and add the GitHub OIDC publisher for this repository.
2. Push a version tag (for example, `v0.1.0`).
3. The `publish-pypi` workflow will build and upload the distribution to PyPI.

### Release checklist

1. Bump `[project].version` in `pyproject.toml` using semver (`X.Y.Z`).
2. Create and push a matching tag: `vX.Y.Z`.
3. Confirm GitHub Actions `publish-pypi` succeeds.
4. Verify install paths:
   - `uv tool install nuv && nuv --help`
   - `uvx nuv --help`
   - `uvx nuv new smoke --at /tmp/nuv-smoke && cd /tmp/nuv-smoke && uv run pytest`

After release, install with:

```bash
uv tool install nuv
```
