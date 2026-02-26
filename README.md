# nuv

Scaffold opinionated uv Python projects — tests passing, quality tooling green, out of the box.

```
nuv new my-tool
```

That's it. You get a working project with argparse, logging, 100% test coverage, ruff, and ty all green from commit zero.

## Install

```bash
uv tool install nuv
```

Until the first PyPI release is published, use:

```bash
uv tool install git+https://github.com/stevencarpenter/nuv
```

Or run without installing:

```bash
uvx --from git+https://github.com/stevencarpenter/nuv nuv new my-tool
```

## Usage

```
nuv new <name>                              # creates ./<name>/, syncs deps, installs tool editable
nuv new <name> --at <path>                  # creates at an explicit path
nuv new <name> --install none               # scaffold + sync, skip tool install
nuv new <name> --install command-only       # log install command, do not execute (use --log-level INFO)
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

By default, `nuv new` now also runs `uv tool install --editable <project-path>`, so the `<name>` command (derived from the `<name>` argument, for example `my-tool`) is immediately available on your PATH.

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
2. **Install generated projects** with optional automation for tool installs (editable by default today, with a longer-term goal of keeping scaffolding defaults conservative).

See the design brainstorm and phased proposal in `docs/plans/2026-02-26-two-layer-installation.md`.


## Publishing to PyPI

This project is configured for trusted publishing from GitHub Actions.

1. Create a [PyPI project](https://pypi.org/manage/projects/) named `nuv` and add the GitHub OIDC publisher for this repository.
2. Push a version tag (for example, `v0.1.0`).
3. The `publish-pypi` workflow will build and upload the distribution to PyPI.

After release, install with:

```bash
uv tool install nuv
```
