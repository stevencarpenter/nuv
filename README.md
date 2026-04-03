# nuv

[![PyPI version](https://img.shields.io/pypi/v/nuv?logo=pypi&logoColor=white)](https://pypi.org/project/nuv/)
[![Python versions](https://img.shields.io/pypi/pyversions/nuv?logo=python&logoColor=white)](https://pypi.org/project/nuv/)
[![License](https://img.shields.io/pypi/l/nuv)](https://github.com/stevencarpenter/nuv/blob/main/LICENSE)
[![PyPI monthly downloads](https://img.shields.io/pypi/dm/nuv?logo=pypi&logoColor=white)](https://pypi.org/project/nuv/)
[![Downloads](https://static.pepy.tech/badge/nuv)](https://pepy.tech/project/nuv)
[![Wheel](https://img.shields.io/pypi/wheel/nuv)](https://pypi.org/project/nuv/#files)
[![CI](https://img.shields.io/github/actions/workflow/status/stevencarpenter/nuv/ci.yml?branch=main&label=CI)](https://github.com/stevencarpenter/nuv/actions/workflows/ci.yml)
[![Publish to PyPI](https://img.shields.io/github/actions/workflow/status/stevencarpenter/nuv/publish-pypi.yml?label=publish)](https://github.com/stevencarpenter/nuv/actions/workflows/publish-pypi.yml)
[![Lint: Ruff](https://img.shields.io/badge/lint-ruff-46A2F1?logo=ruff&logoColor=white)](https://docs.astral.sh/ruff/)
[![Types: ty](https://img.shields.io/badge/types-ty-0F766E)](https://github.com/astral-sh/ty)

Scaffold opinionated [uv](https://docs.astral.sh/uv/) Python projects — tests passing, linting green, out of the box.

```
nuv new my-tool
```

That's it. You get a working project with argparse, logging, test coverage, ruff, and ty — all green from commit zero.

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
nuv new <name> --archetype spark            # PySpark 4 project with notebooks
nuv new <name> --archetype fastapi          # FastAPI + Granian + Docker
nuv new <name> --python-version 3.13        # override default Python version
nuv new <name> --install none               # scaffold + sync, skip tool install
nuv new <name> --install command-only       # log install command, do not execute (default)
nuv new <name> --keep-on-failure            # keep generated files if sync/install fails
```

## Archetypes

### script (default)

A single-file CLI tool with argparse and logging.

```bash
nuv new my-tool
```

```
my-tool/
├── main.py          # argparse + logging
├── _logging.py
├── pyproject.toml   # pytest, ruff, ty, uv
├── README.md
└── tests/
    ├── __init__.py
    └── test_main.py
```

### spark

A PySpark 4 project with src-layout, chispa testing, and dual notebooks (Jupyter + marimo).

```bash
nuv new my-spark-app --archetype spark
```

```
my-spark-app/
├── main.py
├── pyproject.toml
├── README.md
├── src/my_spark_app/
│   ├── __init__.py
│   ├── _logging.py
│   ├── config.py
│   ├── session.py
│   └── jobs/
│       ├── __init__.py
│       └── example.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   └── test_example.py
└── notebooks/
    ├── explore.ipynb
    └── explore_marimo.py
```

Default Python version: 3.13 (PySpark 4 compatibility).

```bash
uv run pytest          # 8 tests, passing
uv run ruff check .    # clean
uv run ty check        # clean
```

Notebooks are an optional dependency group:

```bash
uv sync --group notebooks
uv run jupyter lab notebooks/
uv run marimo run notebooks/explore_marimo.py
```

### fastapi

A production-ready FastAPI project with Granian ASGI server, Pydantic settings, and a multi-stage Dockerfile.

```bash
nuv new my-api --archetype fastapi
```

```
my-api/
├── main.py                         # Granian server entry point
├── pyproject.toml
├── README.md
├── Dockerfile                      # multi-stage build
├── .dockerignore
├── src/my_api/
│   ├── __init__.py
│   ├── app.py                      # FastAPI factory with lifespan
│   ├── config.py                   # Pydantic settings from env vars
│   ├── _logging.py
│   ├── dependencies.py             # shared FastAPI deps
│   └── routes/
│       ├── __init__.py
│       └── health.py               # /healthz endpoint
└── tests/
    ├── __init__.py
    ├── conftest.py                  # async httpx client fixture
    └── test_health.py
```

Default Python version: 3.14.

```bash
uv run pytest          # passing
uv run ruff check .    # clean
uv run ty check        # clean
```

Run locally:

```bash
uv run python main.py
uv run python main.py --host 0.0.0.0 --port 8000
```

Docker:

```bash
docker build -t my-api .
docker run -p 8000:8000 my-api
```

## Quality out of the box

Every generated project ships with these tools configured and green:

| Tool | Config |
|---|---|
| pytest | branch coverage enforced |
| ruff | lint + format |
| ty | type checking |

By default, `nuv new` logs the command you can run to install the generated project as a tool:

```bash
uv tool install --editable <project-path>
```

## Why

`uv init` produces a stub. The gap between that and "actually writing code" is annoying when you create projects frequently. `nuv` closes it.

## Publishing to PyPI

This project uses trusted publishing from GitHub Actions.

1. Bump `[project].version` in `pyproject.toml`.
2. Push a matching tag: `vX.Y.Z`.
3. GitHub Actions builds and publishes to PyPI.

After release:

```bash
uv tool install nuv
```
