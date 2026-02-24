# nuv — Design Document

**Date:** 2026-02-24
**Status:** Approved

## Overview

`nuv` is a standalone installable uv tool that scaffolds new isolated Python uv projects with an opinionated, ready-to-run structure. It lives in its own repository and is installed once via:

```bash
uv tool install git+https://github.com/you/nuv
```

After that, `nuv new my-project` creates a fully wired project in seconds — argument parsing, logging, constants, passing tests, and all quality tools green out of the box.

## Motivation

`uv init` produces a useless stub. The gap between `uv init` and "actually writing code" is too wide for a playground repo where projects are created frequently and abandoned or iterated freely. `nuv` closes that gap.

## Command Interface

```
nuv new <name>              # creates ./name/ in cwd
nuv new <name> --at <path>  # creates at an explicit path
```

`nuv` is the command root, designed as a namespace for future subcommands.

## Repository Layout

```
nuv/
├── pyproject.toml
├── src/
│   └── nuv/
│       ├── __init__.py
│       ├── cli.py                  # argument parsing, subcommand dispatch
│       ├── commands/
│       │   └── new.py              # nuv new logic
│       └── templates/
│           ├── main.py.tpl         # main.py template
│           ├── pyproject.toml.tpl  # pyproject.toml template
│           ├── readme.md.tpl       # README.md template
│           └── test_main.py.tpl    # tests/test_main.py template
└── tests/
    └── test_new.py
```

## `nuv new` Behavior

1. Validate `<name>`: alphanumeric + hyphens/underscores, no spaces, no existing dir collision
2. Resolve target directory (cwd/name or explicit --at path)
3. `mkdir` the target
4. Render all templates via `string.Template` (substituting `$name`, `$module_name`)
5. Write: `pyproject.toml`, `main.py`, `README.md`, `tests/__init__.py`, `tests/test_main.py`
6. Shell out: `uv sync` inside the new dir to generate `uv.lock` + `.venv`
7. Print: `created my-project/`

On any failure: print a clean error to stderr, exit 1. Cases handled: invalid name, directory already exists, `uv` not found on PATH, `uv sync` non-zero exit.

## Generated `main.py` Convention

```python
import argparse
import logging
import sys
from typing import Sequence

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

PROJECT_NAME = "$name"

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="TODO")
    parser.add_argument(
        "--log-level",
        default="WARNING",
        choices=("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"),
        help="Logging level (default: WARNING).",
    )
    return parser


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    return build_parser().parse_args(argv)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    logging.basicConfig(
        level=args.log_level,
        format="%(levelname)s %(name)s: %(message)s",
        stream=sys.stderr,
    )
    log.debug("Starting %s", PROJECT_NAME)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

## Generated `pyproject.toml`

```toml
[project]
name = "$name"
version = "0.1.0"
description = ""
readme = "README.md"
requires-python = ">=3.14"
dependencies = []

[dependency-groups]
dev = [
    "pytest>=8",
    "pytest-cov>=6",
    "ruff>=0.9",
    "ty>=0.0.1a1",
]
```

## Generated `tests/test_main.py`

```python
from main import main


def test_main_returns_zero() -> None:
    assert main([]) == 0
```

After `nuv new`, all of the following pass immediately:

```bash
uv run pytest
uv run ruff check .
uv run ty check
```

## Quality — `nuv` Tool Itself

| Tool | Config |
|---|---|
| pytest | 100% coverage enforced (`--cov-fail-under=100`) |
| ruff | lint + format |
| ty | type checking |

## `nuv` Own `pyproject.toml`

```toml
[project]
name = "nuv"
version = "0.1.0"
requires-python = ">=3.14"
dependencies = []

[project.scripts]
nuv = "nuv.cli:main"

[dependency-groups]
dev = [
    "pytest>=8",
    "pytest-cov>=6",
    "ruff>=0.9",
    "ty>=0.0.1a1",
]
```

## Non-Goals

- No workspace integration (each generated project is fully isolated)
- No ENV sourcing or dotenv in generated projects (deferred)
- No interactive prompts (all config via CLI args)
- No PyPI publishing of `nuv` (git install only)
