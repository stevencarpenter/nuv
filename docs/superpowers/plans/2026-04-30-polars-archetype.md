# Polars + DuckDB + Delta Local Data Lake Archetype Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a `polars` archetype to nuv that scaffolds a local data lake project using Polars, DuckDB, Delta Lake, marimo notebooks, and a click CLI.

**Architecture:** Register `"polars"` in VALID_ARCHETYPES and DEFAULT_PYTHON_VERSIONS. Add `_scaffold_polars()` to new.py, add dispatch in `scaffold_files()`. 13 template files in `src/nuv/templates/polars/`. Update `cli.py` choices. Test the archetype in `test_new.py`.

**Tech Stack:** nuv (existing), Polars, DuckDB, Delta Lake, click, marimo, hatchling, pytest, ruff, ty

---

### Task 1: Register polars archetype + update CLI

**Files:**
- Modify: `src/nuv/commands/new.py:27`
- Modify: `src/nuv/commands/new.py:142`
- Modify: `src/nuv/cli.py:34`
- Modify: `src/nuv/cli.py:43`

- [ ] **Step 1: Add `"polars"` to DEFAULT_PYTHON_VERSIONS**

```python
DEFAULT_PYTHON_VERSIONS = {"script": "3.14", "spark": "3.13", "fastapi": "3.14", "polars": "3.14"}
```

- [ ] **Step 2: Add `"polars"` to VALID_ARCHETYPES**

```python
VALID_ARCHETYPES = ("script", "spark", "fastapi", "polars")
```

- [ ] **Step 3: Add `"polars"` to the argeparse choices in cli.py**

```python
choices=["script", "spark", "fastapi", "polars"],
```

- [ ] **Step 4: Update help text to mention polars**

```python
help="Python version (default depends on archetype — script=3.14, spark=3.13, fastapi=3.14, polars=3.14). Must be MAJOR.MINOR format.",
```

- [ ] **Step 5: Run existing tests to confirm nothing broke**

Run: `uv run pytest tests/test_new.py -v`
Expected: all tests pass

- [ ] **Step 6: Commit**

```bash
git add src/nuv/commands/new.py src/nuv/cli.py
git commit -m "feat: register polars archetype in registry and CLI choices"
```

---

### Task 2: Create polars template files — config, pyproject, gitignore, readme, logging

**Files:**
- Create: `src/nuv/templates/polars/__init__.py.tpl` — empty
- Create: `src/nuv/templates/polars/init.py.tpl` — empty (for src/{module}/__init__.py)
- Create: `src/nuv/templates/polars/pyproject.toml.tpl`
- Create: `src/nuv/templates/polars/gitignore.tpl`
- Create: `src/nuv/templates/polars/readme.md.tpl`
- Create: `src/nuv/templates/polars/_logging.py.tpl`
- Create: `src/nuv/templates/polars/config.py.tpl`

- [ ] **Step 1: Create `pyproject.toml.tpl`**

```toml
[project]
name = "{name}"
version = "0.1.0"
description = ""
readme = "README.md"
requires-python = ">={python_version}"
dependencies = [
    "polars>=1",
    "duckdb>=1",
    "deltalake>=0.20",
    "pydantic-settings>=2",
    "click>=8",
]

[project.scripts]
{name} = "{module_name}.main:main"

[dependency-groups]
dev = [
    "pytest>=8",
    "pytest-cov>=6",
    "ruff>=0.9",
    "ty>=0.0.1a1",
]
notebooks = [
    "marimo>=0.10",
]

[tool.uv]
managed = true

[tool.pytest.ini_options]
addopts = "--cov=main --cov={module_name} --cov-report=term-missing --cov-fail-under=90"

[tool.ruff]
target-version = "py{python_version_nodot}"
line-length = 180

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B", "SIM"]

[tool.coverage.run]
branch = true

[tool.coverage.report]
exclude_lines = ["if __name__ == .__main__.:"]

[tool.hatch.build.targets.wheel]
packages = ["src/{module_name}"]
include = ["main.py"]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

- [ ] **Step 2: Create `gitignore.tpl`** — copy from spark's gitignore.tpl and add `data/` and `warehouse.db`

Same content as `src/nuv/templates/spark/gitignore.tpl` plus these delta-specific entries:
```
data/
warehouse.db
_delta_log/
```

- [ ] **Step 3: Create `readme.md.tpl`**

```markdown
# {name}

## Setup

```bash
uv sync
```

### Notebooks (optional)

```bash
uv sync --group notebooks
```

## Usage

```bash
uv run python main.py --help
uv run python main.py --log-level INFO
```

## Development

```bash
uv run pytest          # run tests
uv run ruff check .    # lint
uv run ruff format .   # format
uv run ty check .      # type check
```

## Notebooks

```bash
uv run marimo edit notebooks/explore.py
```
```

- [ ] **Step 4: Create `_logging.py.tpl`**

```python
import logging
import sys

LOG_FORMAT = "%(levelname)s %(name)s: %(message)s"


def configure(level: str = "WARNING") -> None:
    logging.basicConfig(
        level=level,
        format=LOG_FORMAT,
        stream=sys.stderr,
    )
```

- [ ] **Step 5: Create `config.py.tpl`**

```python
from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "{name}"
    log_level: str = "INFO"
    data_root: Path = Path("data")
```

- [ ] **Step 6: Create `__init__.py.tpl` and `init.py.tpl`** — both empty files (single blank line)

- [ ] **Step 7: Verify templates render correctly**

```bash
uv run python -c "
from nuv.commands.new import render_template
for tpl in ['pyproject.toml.tpl', 'gitignore.tpl', 'readme.md.tpl', '_logging.py.tpl', 'config.py.tpl']:
    result = render_template(tpl, archetype='polars', name='test-polars', module_name='test_polars')
    print(f'{tpl}: OK ({len(result)} chars)')
"
```

Expected: all 5 templates render without KeyError.

- [ ] **Step 8: Commit**

```bash
git add src/nuv/templates/polars/
git commit -m "feat: add polars template files (config, pyproject, gitignore, readme, logging)"
```

---

### Task 3: Create polars template files — _io, _db, main, explore notebook

**Files:**
- Create: `src/nuv/templates/polars/main.py.tpl`
- Create: `src/nuv/templates/polars/_io.py.tpl`
- Create: `src/nuv/templates/polars/_db.py.tpl`
- Create: `src/nuv/templates/polars/notebooks/explore.py.tpl`

- [ ] **Step 1: Create `main.py.tpl`**

```python
import logging

import click

log = logging.getLogger(__name__)


@click.command()
@click.option(
    "--log-level",
    default="WARNING",
    show_default=True,
    help="Logging level.",
)
def main(log_level: str) -> None:
    from {module_name}._logging import configure
    configure(log_level)
    log.info("Starting {name}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Create `_io.py.tpl`**

```python
from pathlib import Path

import polars as pl


def read_csv(path: str | Path, **kwargs) -> pl.DataFrame:
    return pl.read_csv(path, **kwargs)


def read_parquet(path: str | Path, **kwargs) -> pl.DataFrame:
    return pl.read_parquet(path, **kwargs)


def read_delta(path: str | Path, **kwargs) -> pl.DataFrame:
    return pl.read_delta(path, **kwargs)


def read_json(path: str | Path, **kwargs) -> pl.DataFrame:
    return pl.read_json(path, **kwargs)


def write(df: pl.DataFrame, path: str | Path, **kwargs) -> None:
    path = Path(path)
    suffix = path.suffix.lower()
    if suffix == ".csv":
        df.write_csv(path, **kwargs)
    elif suffix == ".parquet":
        df.write_parquet(path, **kwargs)
    elif suffix == ".json":
        df.write_json(path, **kwargs)
    else:
        raise ValueError(f"Unsupported format: {suffix}")


def write_delta(df: pl.DataFrame, path: str | Path, mode: str = "overwrite", **kwargs) -> None:
    df.write_delta(path, mode=mode, **kwargs)


def show(df: pl.DataFrame, max_rows: int = 20) -> None:
    print(df.head(max_rows))


def glimpse(df: pl.DataFrame) -> None:
    n_rows = df.height
    n_cols = df.width
    print(f"Rows: {n_rows:,}    Columns: {n_cols:,}")
    print(dict(df.schema))
```

- [ ] **Step 3: Create `_db.py.tpl`**

```python
from pathlib import Path

import duckdb
import polars as pl


def sql(query: str) -> pl.DataFrame:
    return duckdb.sql(query).pl()
```

- [ ] **Step 4: Create `notebooks/explore.py.tpl`**

```python
import marimo

__generated_with = "0.10.0"
app = marimo.App(width="medium")


@app.cell
def _():
    import polars as pl

    from {module_name}._io import read_csv, read_parquet, show, glimpse
    from {module_name}._db import sql

    pl
    return (pl, read_csv, read_parquet, show, glimpse, sql)


@app.cell
def _(pl):
    df = pl.DataFrame({"x": [1, 2, 3], "y": ["a", "b", "c"]})
    df
    return (df,)


if __name__ == "__main__":
    app.run()
```

- [ ] **Step 5: Verify new templates render**

```bash
uv run python -c "
from nuv.commands.new import render_template
for tpl in ['main.py.tpl', '_io.py.tpl', '_db.py.tpl']:
    result = render_template(tpl, archetype='polars', name='test-polars', module_name='test_polars')
    print(f'{tpl}: OK ({len(result)} chars)')
"
```

Expected: all templates render without KeyError.

- [ ] **Step 6: Commit**

```bash
git add src/nuv/templates/polars/
git commit -m "feat: add polars template files (_io, _db, main, notebook)"
```

---

### Task 4: Create polars template files — tests

**Files:**
- Create: `src/nuv/templates/polars/tests/__init__.py.tpl` — empty
- Create: `src/nuv/templates/polars/tests/conftest.py.tpl`
- Create: `src/nuv/templates/polars/tests/test_io.py.tpl`

- [ ] **Step 1: Create `tests/__init__.py.tpl`** — empty file (single blank line)

- [ ] **Step 2: Create `conftest.py.tpl`**

```python
import polars as pl
import pytest


@pytest.fixture
def sample_df() -> pl.DataFrame:
    return pl.DataFrame({"x": [1, 2, 3], "y": ["a", "b", "c"]})
```

- [ ] **Step 3: Create `test_io.py.tpl`**

```python
import polars as pl
from polars.testing import assert_frame_equal

from {module_name}._io import (
    glimpse,
    read_csv,
    read_delta,
    read_json,
    read_parquet,
    show,
    write,
    write_delta,
)


def test_read_parquet_roundtrip(tmp_path):
    df = pl.DataFrame({"x": [1, 2, 3], "y": ["a", "b", "c"]})
    path = tmp_path / "test.parquet"
    write(df, path)
    result = read_parquet(path)
    assert_frame_equal(result, df)


def test_read_csv_roundtrip(tmp_path):
    df = pl.DataFrame({"x": [1, 2, 3], "y": ["a", "b", "c"]})
    path = tmp_path / "test.csv"
    write(df, path)
    result = read_csv(path)
    assert_frame_equal(result, df)


def test_read_json_roundtrip(tmp_path):
    df = pl.DataFrame({"x": [1, 2, 3], "y": ["a", "b", "c"]})
    path = tmp_path / "test.json"
    write(df, path)
    result = read_json(path)
    assert_frame_equal(result, df)


def test_write_unsupported_format(sample_df, tmp_path):
    path = tmp_path / "test.xyz"
    result = write(sample_df, path)
    assert result is None


def test_read_delta_roundtrip(tmp_path):
    df = pl.DataFrame({"x": [1, 2, 3], "y": ["a", "b", "c"]})
    path = tmp_path / "delta-table"
    write_delta(df, path)
    result = read_delta(path)
    assert_frame_equal(result, df)


def test_show_does_not_raise(sample_df):
    show(sample_df)


def test_glimpse_does_not_raise(sample_df):
    glimpse(sample_df)
```

- [ ] **Step 4: Verify test templates render**

```bash
uv run python -c "
from nuv.commands.new import render_template
for tpl in ['conftest.py.tpl', 'test_io.py.tpl']:
    result = render_template(tpl, archetype='polars', name='test', module_name='test_polars')
    print(f'{tpl}: OK ({len(result)} chars)')
"
```

Expected: both render without error.

- [ ] **Step 5: Commit**

```bash
git add src/nuv/templates/polars/
git commit -m "feat: add polars template files (tests)"
```

---

### Task 5: Add _scaffold_polars function + update scaffold_files dispatch

**Files:**
- Modify: `src/nuv/commands/new.py`

- [ ] **Step 1: Add `_scaffold_polars` function to new.py** (after `_scaffold_fastapi`, before `run_uv_sync`)

```python
def _scaffold_polars(
    target: Path,
    *,
    template_vars: dict[str, str],
    module_name: str,
) -> None:
    # src/<module_name>/ package
    pkg_dir = target / "src" / module_name
    pkg_dir.mkdir(parents=True)
    write_with_trailing_newline(pkg_dir / "__init__.py", render_template("init.py.tpl", **template_vars))
    write_with_trailing_newline(pkg_dir / "_logging.py", render_template("_logging.py.tpl", **template_vars))
    write_with_trailing_newline(pkg_dir / "_io.py", render_template("_io.py.tpl", **template_vars))
    write_with_trailing_newline(pkg_dir / "_db.py", render_template("_db.py.tpl", **template_vars))
    write_with_trailing_newline(pkg_dir / "config.py", render_template("config.py.tpl", **template_vars))
    write_with_trailing_newline(pkg_dir / "main.py", render_template("main.py.tpl", **template_vars))

    # tests/
    tests_dir = target / "tests"
    write_with_trailing_newline(tests_dir / "conftest.py", render_template("conftest.py.tpl", **template_vars))
    write_with_trailing_newline(tests_dir / "test_io.py", render_template("test_io.py.tpl", **template_vars))

    # notebooks/
    notebooks_dir = target / "notebooks"
    notebooks_dir.mkdir()
    write_with_trailing_newline(notebooks_dir / "explore.py", render_template("notebooks/explore.py.tpl", **template_vars))

    # data/ directories
    (target / "data" / "raw").mkdir(parents=True)
    (target / "data" / "features").mkdir(parents=True)
```

- [ ] **Step 2: Update `scaffold_files` to dispatch polars** (replace `else:  # fastapi` comment block)

Change the final `else`:
```python
elif archetype == "fastapi":
    _scaffold_fastapi(target, template_vars=template_vars, name=name, module_name=module_name)
elif archetype == "polars":
    _scaffold_polars(target, template_vars=template_vars, module_name=module_name)
```

This means the else-branch becomes explicit branches. The full dispatch section after the shared files block becomes:

```python
    if archetype == "script":
        write_with_trailing_newline(target / "_logging.py", render_template("_logging.py.tpl", **template_vars))
        write_with_trailing_newline(tests_dir / "test_main.py", render_template("test_main.py.tpl", **template_vars))
    elif archetype == "spark":
        _scaffold_spark(target, template_vars=template_vars, name=name, module_name=module_name)
    elif archetype == "fastapi":
        _scaffold_fastapi(target, template_vars=template_vars, name=name, module_name=module_name)
    elif archetype == "polars":
        _scaffold_polars(target, template_vars=template_vars, module_name=module_name)
```

- [ ] **Step 3: Run existing tests to confirm scaffold_files dispatch still works**

Run: `uv run pytest tests/test_new.py -v`
Expected: all 70+ tests pass

- [ ] **Step 4: Commit**

```bash
git add src/nuv/commands/new.py
git commit -m "feat: add _scaffold_polars and dispatch from scaffold_files"
```

---

### Task 6: Add tests for polars archetype in test_new.py

**Files:**
- Modify: `tests/test_new.py`

- [ ] **Step 1: Add test for polars DEFAULT_PYTHON_VERSIONS entry**

```python
def test_default_python_versions_polars() -> None:
    assert DEFAULT_PYTHON_VERSIONS["polars"] == "3.14"
```

- [ ] **Step 2: Add test for polars scaffold_files creates expected files**

```python
def test_scaffold_files_polars_creates_expected_files(tmp_path: Path) -> None:
    target = tmp_path / "my-polars-app"
    target.mkdir()
    scaffold_files(target, name="my-polars-app", module_name="my_polars_app", archetype="polars")

    assert (target / ".python-version").exists()
    assert (target / ".gitignore").exists()
    assert (target / "main.py").exists()
    assert (target / "pyproject.toml").exists()
    assert (target / "README.md").exists()
    assert (target / "src" / "my_polars_app" / "__init__.py").exists()
    assert (target / "src" / "my_polars_app" / "_logging.py").exists()
    assert (target / "src" / "my_polars_app" / "_io.py").exists()
    assert (target / "src" / "my_polars_app" / "_db.py").exists()
    assert (target / "src" / "my_polars_app" / "config.py").exists()
    assert (target / "src" / "my_polars_app" / "main.py").exists()
    assert (target / "tests" / "__init__.py").exists()
    assert (target / "tests" / "conftest.py").exists()
    assert (target / "tests" / "test_io.py").exists()
    assert (target / "notebooks" / "explore.py").exists()
    assert (target / "data" / "raw").exists()
    assert (target / "data" / "features").exists()
```

- [ ] **Step 3: Add test for polars pyproject dependencies**

```python
def test_scaffold_files_polars_pyproject_has_deps(tmp_path: Path) -> None:
    target = tmp_path / "my-polars-app"
    target.mkdir()
    scaffold_files(target, name="my-polars-app", module_name="my_polars_app", archetype="polars")
    pyproject = (target / "pyproject.toml").read_text()
    assert "polars>=1" in pyproject
    assert "duckdb>=1" in pyproject
    assert "deltalake>=0.20" in pyproject
    assert "pydantic-settings>=2" in pyproject
    assert "click>=8" in pyproject
    assert "marimo>=0.10" in pyproject
    assert "py314" in pyproject
    assert 'packages = ["src/my_polars_app"]' in pyproject
    assert 'build-backend = "hatchling.build"' in pyproject
```

- [ ] **Step 4: Add test for polars main imports**

```python
def test_scaffold_files_polars_main_uses_click(tmp_path: Path) -> None:
    target = tmp_path / "my-polars-app"
    target.mkdir()
    scaffold_files(target, name="my-polars-app", module_name="my_polars_app", archetype="polars")
    main_content = (target / "main.py").read_text()
    assert "import click" in main_content
    assert "@click.command()" in main_content
```

- [ ] **Step 5: Add test for polars uses click in package main (not argparse)**

```python
def test_scaffold_files_polars_package_main_has_io_imports(tmp_path: Path) -> None:
    target = tmp_path / "my-polars-app"
    target.mkdir()
    scaffold_files(target, name="my-polars-app", module_name="my_polars_app", archetype="polars")
    io_content = (target / "src" / "my_polars_app" / "_io.py").read_text()
    assert "read_csv" in io_content
    assert "read_parquet" in io_content
    assert "show" in io_content
    assert "glimpse" in io_content
    db_content = (target / "src" / "my_polars_app" / "_db.py").read_text()
    assert "import duckdb" in db_content
```

- [ ] **Step 6: Add test for polars trailing newlines**

```python
def test_scaffold_files_polars_end_with_trailing_newline(tmp_path: Path) -> None:
    target = tmp_path / "my-polars-app"
    target.mkdir()
    scaffold_files(target, name="my-polars-app", module_name="my_polars_app", archetype="polars")

    generated_files = [
        ".python-version",
        ".gitignore",
        "main.py",
        "pyproject.toml",
        "README.md",
        "src/my_polars_app/__init__.py",
        "src/my_polars_app/_logging.py",
        "src/my_polars_app/_io.py",
        "src/my_polars_app/_db.py",
        "src/my_polars_app/config.py",
        "src/my_polars_app/main.py",
        "tests/__init__.py",
        "tests/conftest.py",
        "tests/test_io.py",
        "notebooks/explore.py",
    ]

    for rel_path in generated_files:
        content = (target / rel_path).read_text()
        assert content.endswith("\n"), f"Expected trailing newline in {rel_path}"
```

- [ ] **Step 7: Add integration test — run_new polars success**

```python
def test_run_new_polars_success(tmp_path: Path) -> None:
    with (
        patch("nuv.commands.new.shutil.which", return_value="/usr/bin/uv"),
        patch("nuv.commands.new.subprocess.run") as mock_run,
    ):
        mock_run.return_value = MagicMock(returncode=0)
        result = run_new("my-polars-app", at=str(tmp_path / "my-polars-app"), cwd=tmp_path, archetype="polars")
    assert result == 0
    assert (tmp_path / "my-polars-app" / "main.py").exists()
    assert (tmp_path / "my-polars-app" / "src" / "my_polars_app" / "_io.py").exists()
    assert (tmp_path / "my-polars-app" / "notebooks" / "explore.py").exists()
    assert (tmp_path / "my-polars-app" / "data" / "raw").exists()
```

- [ ] **Step 8: Add integration test — polars cleanup on failure**

```python
def test_run_new_polars_cleanup_on_failure(tmp_path: Path) -> None:
    with patch("nuv.commands.new.shutil.which", return_value=None):
        result = run_new("my-polars-app", cwd=tmp_path, archetype="polars")
    assert result == 1
    assert not (tmp_path / "my-polars-app").exists()


def test_run_new_polars_keep_on_failure(tmp_path: Path) -> None:
    with patch("nuv.commands.new.shutil.which", return_value=None):
        result = run_new("my-polars-app", cwd=tmp_path, archetype="polars", keep_on_failure=True)
    assert result == 1
    assert (tmp_path / "my-polars-app").exists()
```

- [ ] **Step 9: Add CLI test — new with polars archetype**

```python
def test_cli_new_polars_archetype(tmp_path: Path) -> None:
    with (
        patch("nuv.commands.new.shutil.which", return_value="/usr/bin/uv"),
        patch("nuv.commands.new.subprocess.run") as mock_run,
    ):
        mock_run.return_value = MagicMock(returncode=0)
        result = cli_main(["new", "my-polars-app", "--at", str(tmp_path / "my-polars-app"), "--archetype", "polars"])
    assert result == 0
    assert (tmp_path / "my-polars-app" / "src" / "my_polars_app" / "__init__.py").exists()
    assert (tmp_path / "my-polars-app" / "data" / "raw").exists()


def test_cli_polars_default_python_version(tmp_path: Path) -> None:
    with (
        patch("nuv.commands.new.shutil.which", return_value="/usr/bin/uv"),
        patch("nuv.commands.new.subprocess.run") as mock_run,
    ):
        mock_run.return_value = MagicMock(returncode=0)
        result = cli_main(["new", "my-polars-app", "--at", str(tmp_path / "my-polars-app"), "--archetype", "polars"])
    assert result == 0
    assert (tmp_path / "my-polars-app" / ".python-version").read_text().strip() == "3.14"
```

- [ ] **Step 10: Add polars default version test**

```python
def test_run_new_polars_uses_default_python_314(tmp_path: Path) -> None:
    with (
        patch("nuv.commands.new.shutil.which", return_value="/usr/bin/uv"),
        patch("nuv.commands.new.subprocess.run") as mock_run,
        patch("nuv.commands.new.scaffold_files") as mock_scaffold,
    ):
        mock_run.return_value = MagicMock(returncode=0)
        result = run_new("my-polars-app", at=str(tmp_path / "my-polars-app"), cwd=tmp_path, archetype="polars")
    assert result == 0
    mock_scaffold.assert_called_once()
    call_kwargs = mock_scaffold.call_args[1]
    assert call_kwargs["python_version"] == "3.14"
    assert call_kwargs["archetype"] == "polars"
```

- [ ] **Step 11: Run all tests to confirm everything passes**

```bash
uv run pytest tests/test_new.py -v
```

Expected: all tests pass, including existing (non-polars) and new polars tests.

Expected test count: approximately 85+ tests (70 existing + ~15 new polars tests).

- [ ] **Step 12: Check coverage hasn't dropped**

```bash
uv run pytest tests/test_new.py --cov=nuv.commands.new --cov-report=term-missing
```

Expected: branch coverage >= 92%.

- [ ] **Step 13: Verify the archetype description in CLI** — check that `nuv new --help` shows `polars`

```bash
uv run python -c "from nuv.cli import build_parser; parser = build_parser(); parser.parse_args(['new', '--help'])"
```

Expected: help output includes "polars" as a choice for --archetype.

- [ ] **Step 14: Commit**

```bash
git add tests/test_new.py
git commit -m "test: add polars archetype tests"
```