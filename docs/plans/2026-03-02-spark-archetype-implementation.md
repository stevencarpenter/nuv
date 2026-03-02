# Spark Archetype Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add a `spark` archetype to nuv that generates a fully configured PySpark 4 project with src-layout package, chispa testing, dual notebooks, and a CLI-args-to-env-vars config resolver.

**Architecture:** New template set at `src/nuv/templates/spark/`, archetype-aware branching in `scaffold_files()`, and a programmatic Jupyter notebook generator (since `.ipynb` JSON conflicts with `str.format()` braces). All existing validation, `run_uv_sync`, and `run_tool_install` logic is reused unchanged.

**Tech Stack:** Python 3.11+ (nuv itself), PySpark 4.0, chispa, pytest, ruff, ty, hatchling, Jupyter, marimo

**Design doc:** `docs/plans/2026-03-02-spark-archetype-design.md`

---

### Task 1: Create Spark Template Directory

**Files:**
- Create: `src/nuv/templates/spark/__init__.py`

**Step 1: Create directory and empty __init__.py**

```bash
mkdir -p src/nuv/templates/spark
touch src/nuv/templates/spark/__init__.py
```

**Step 2: Commit**

```bash
git add src/nuv/templates/spark/__init__.py
git commit -m "feat(spark): create spark template directory"
```

---

### Task 2: Create Spark Template Files — Scaffolding Primitives

These are text templates consumed by the existing `render_template()` function. They use `str.format()` with variables: `{name}`, `{module_name}`, `{python_version}`, `{python_version_nodot}`.

**Files:**
- Create: `src/nuv/templates/spark/gitignore.tpl`
- Create: `src/nuv/templates/spark/init.py.tpl`
- Create: `src/nuv/templates/spark/jobs_init.py.tpl`

**Step 1: Create gitignore.tpl**

File: `src/nuv/templates/spark/gitignore.tpl`

```
.idea/
*.iml
.vscode/
.DS_Store
.directory
*.swp
*.swo
*~
.claude/
.codex/
.copilot/
.amp/
.opencode/
.venv/
__pycache__/
*.pyc
*.pyo
.pytest_cache/
.coverage
htmlcov/
dist/
*.egg-info/
.uv/
.uvx/
.ruff_cache/
derby.log
metastore_db/
spark-warehouse/
*.parquet
*.snappy
.ipynb_checkpoints/
```

**Step 2: Create init.py.tpl** (empty `__init__.py` for the package)

File: `src/nuv/templates/spark/init.py.tpl`

```
```

(Empty file — just a trailing newline will be added by `write_with_trailing_newline`.)

**Step 3: Create jobs_init.py.tpl** (empty `__init__.py` for jobs subpackage)

File: `src/nuv/templates/spark/jobs_init.py.tpl`

```
```

(Same — empty.)

**Step 4: Commit**

```bash
git add src/nuv/templates/spark/gitignore.tpl src/nuv/templates/spark/init.py.tpl src/nuv/templates/spark/jobs_init.py.tpl
git commit -m "feat(spark): add gitignore and init templates"
```

---

### Task 3: Create Spark _logging.py Template

**Files:**
- Create: `src/nuv/templates/spark/_logging.py.tpl`

**Step 1: Create _logging.py.tpl**

File: `src/nuv/templates/spark/_logging.py.tpl`

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
    for name in ("py4j", "pyspark", "org.apache.spark"):
        logging.getLogger(name).setLevel(logging.WARNING)
```

**Step 2: Verify it renders**

```bash
uv run python -c "
from nuv.commands.new import render_template
result = render_template('_logging.py.tpl', archetype='spark', name='test', module_name='test')
assert 'py4j' in result
assert 'pyspark' in result
print('OK')
"
```

Expected: `OK`

**Step 3: Commit**

```bash
git add src/nuv/templates/spark/_logging.py.tpl
git commit -m "feat(spark): add logging template with Spark noise suppression"
```

---

### Task 4: Create Spark config.py Template

**Files:**
- Create: `src/nuv/templates/spark/config.py.tpl`

**Step 1: Create config.py.tpl**

File: `src/nuv/templates/spark/config.py.tpl`

```python
"""Resolve parameters from CLI args, environment variables, and defaults."""

import argparse
import os
from collections.abc import Sequence

DEFAULTS: dict[str, str] = {{
    "env": "dev",
    "job": "example",
    "log_level": "WARNING",
}}


def resolve_params(argv: Sequence[str] | None = None) -> dict[str, str]:
    parser = argparse.ArgumentParser(description="{name}")
    parser.add_argument("--env", default=None, help="Environment (default: dev).")
    parser.add_argument("--job", default=None, help="Job to run (default: example).")
    parser.add_argument(
        "--log-level",
        dest="log_level",
        default=None,
        choices=("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"),
        help="Logging level (default: WARNING).",
    )
    parsed = parser.parse_args(argv)

    params: dict[str, str] = {{}}
    for key, default in DEFAULTS.items():
        cli_val = getattr(parsed, key, None)
        env_val = os.environ.get(f"SPARK_APP_{{key.upper()}}")
        params[key] = cli_val or env_val or default
    return params
```

Note: `{{` and `}}` are literal braces in `str.format()` — they render as `{` and `}` in the output.

**Step 2: Verify it renders**

```bash
uv run python -c "
from nuv.commands.new import render_template
result = render_template('config.py.tpl', archetype='spark', name='my-app', module_name='my_app')
assert 'my-app' in result
assert 'DEFAULTS: dict[str, str] = {' in result
assert '{{' not in result  # no double braces in output
print('OK')
"
```

Expected: `OK`

**Step 3: Commit**

```bash
git add src/nuv/templates/spark/config.py.tpl
git commit -m "feat(spark): add config template with CLI/env parameter resolution"
```

---

### Task 5: Create Spark session.py Template

**Files:**
- Create: `src/nuv/templates/spark/session.py.tpl`

**Step 1: Create session.py.tpl**

File: `src/nuv/templates/spark/session.py.tpl`

```python
"""Create and configure SparkSession."""

from pyspark.sql import SparkSession


def create_spark_session(app_name: str) -> SparkSession:
    return (
        SparkSession.builder
        .appName(app_name)
        .master("local[*]")
        .getOrCreate()
    )
```

**Step 2: Commit**

```bash
git add src/nuv/templates/spark/session.py.tpl
git commit -m "feat(spark): add session template with SparkSession factory"
```

---

### Task 6: Create Spark jobs/example.py Template

**Files:**
- Create: `src/nuv/templates/spark/example_job.py.tpl`

**Step 1: Create example_job.py.tpl**

File: `src/nuv/templates/spark/example_job.py.tpl`

```python
"""Example Spark job."""

from pyspark.sql import DataFrame, SparkSession


def run(spark: SparkSession, params: dict[str, str]) -> DataFrame:
    data = [("alice", 1), ("bob", 2), ("charlie", 3)]
    df = spark.createDataFrame(data, ["name", "value"])
    return transform(df)


def transform(df: DataFrame) -> DataFrame:
    return df.filter(df.value > 1)
```

**Step 2: Commit**

```bash
git add src/nuv/templates/spark/example_job.py.tpl
git commit -m "feat(spark): add example job template"
```

---

### Task 7: Create Spark main.py Template

**Files:**
- Create: `src/nuv/templates/spark/main.py.tpl`

**Step 1: Create main.py.tpl**

File: `src/nuv/templates/spark/main.py.tpl`

```python
"""Entry point for {name}."""

from {module_name}._logging import configure
from {module_name}.config import resolve_params
from {module_name}.jobs import example
from {module_name}.session import create_spark_session


def main(argv: list[str] | None = None) -> int:
    params = resolve_params(argv)
    configure(params["log_level"])
    spark = create_spark_session("{name}")
    try:
        example.run(spark, params)
    finally:
        spark.stop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

**Step 2: Verify it renders**

```bash
uv run python -c "
from nuv.commands.new import render_template
result = render_template('main.py.tpl', archetype='spark', name='my-spark-app', module_name='my_spark_app')
assert 'from my_spark_app._logging import configure' in result
assert 'from my_spark_app.config import resolve_params' in result
assert 'create_spark_session(\"my-spark-app\")' in result
print('OK')
"
```

Expected: `OK`

**Step 3: Commit**

```bash
git add src/nuv/templates/spark/main.py.tpl
git commit -m "feat(spark): add main entry point template"
```

---

### Task 8: Create Spark pyproject.toml Template

**Files:**
- Create: `src/nuv/templates/spark/pyproject.toml.tpl`

**Step 1: Create pyproject.toml.tpl**

File: `src/nuv/templates/spark/pyproject.toml.tpl`

```toml
[project]
name = "{name}"
version = "0.1.0"
description = ""
readme = "README.md"
requires-python = ">={python_version}"
dependencies = [
    "pyspark>=4,<5",
]

[project.scripts]
{name} = "main:main"

[dependency-groups]
dev = [
    "chispa>=0.11",
    "pytest>=9",
    "pytest-cov>=6",
    "ruff>=0.9",
    "ty>=0.0.1a1",
]
notebooks = [
    "jupyterlab>=4",
    "marimo>=0.10",
]

[tool.uv]
managed = true

[tool.pytest.ini_options]
addopts = "--cov={module_name} --cov-report=term-missing --cov-fail-under=100"

[tool.ruff]
target-version = "py{python_version_nodot}"
line-length = 180

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B", "SIM"]

[tool.coverage.run]
branch = true

[tool.coverage.report]
exclude_lines = ["if __name__ == .__main__.:"]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

**Step 2: Verify it renders**

```bash
uv run python -c "
from nuv.commands.new import render_template
result = render_template('pyproject.toml.tpl', archetype='spark', name='my-spark-app', module_name='my_spark_app')
assert 'pyspark>=4,<5' in result
assert 'chispa>=0.11' in result
assert 'jupyterlab>=4' in result
assert 'marimo>=0.10' in result
print('OK')
"
```

Expected: `OK`

**Step 3: Commit**

```bash
git add src/nuv/templates/spark/pyproject.toml.tpl
git commit -m "feat(spark): add pyproject.toml template with PySpark and notebook deps"
```

---

### Task 9: Create Spark README Template

**Files:**
- Create: `src/nuv/templates/spark/readme.md.tpl`

**Step 1: Create readme.md.tpl**

File: `src/nuv/templates/spark/readme.md.tpl`

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
uv run python main.py --env dev --job example
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
uv run jupyter lab notebooks/      # Jupyter
uv run marimo run notebooks/explore_marimo.py  # marimo
```
```

Note: The triple backticks inside the markdown template are literal — `str.format()` only substitutes `{name}` etc., it doesn't interpret backticks.

**Step 2: Commit**

```bash
git add src/nuv/templates/spark/readme.md.tpl
git commit -m "feat(spark): add README template"
```

---

### Task 10: Create Spark Test Templates

**Files:**
- Create: `src/nuv/templates/spark/conftest.py.tpl`
- Create: `src/nuv/templates/spark/test_example.py.tpl`

**Step 1: Create conftest.py.tpl**

File: `src/nuv/templates/spark/conftest.py.tpl`

```python
import pytest
from pyspark.sql import SparkSession


@pytest.fixture(scope="session")
def spark():
    session = (
        SparkSession.builder
        .master("local[*]")
        .appName("test")
        .config("spark.ui.enabled", "false")
        .getOrCreate()
    )
    yield session
    session.stop()
```

**Step 2: Create test_example.py.tpl**

File: `src/nuv/templates/spark/test_example.py.tpl`

```python
from chispa import assert_df_equality

from {module_name}.jobs.example import transform


def test_transform_filters_low_values(spark):
    source = spark.createDataFrame(
        [("alice", 1), ("bob", 2), ("charlie", 3)],
        ["name", "value"],
    )
    expected = spark.createDataFrame(
        [("bob", 2), ("charlie", 3)],
        ["name", "value"],
    )
    result = transform(source)
    assert_df_equality(result, expected, ignore_row_order=True)
```

**Step 3: Commit**

```bash
git add src/nuv/templates/spark/conftest.py.tpl src/nuv/templates/spark/test_example.py.tpl
git commit -m "feat(spark): add conftest and test_example templates with chispa"
```

---

### Task 11: Create Spark Notebook Templates

**Files:**
- Create: `src/nuv/templates/spark/explore_marimo.py.tpl`
- Modify: `src/nuv/commands/new.py` (add `generate_jupyter_notebook()`)

The `.ipynb` format is JSON with `{` braces everywhere, which conflicts with `str.format()`. Instead of escaping every brace, we generate the notebook programmatically.

**Step 1: Create explore_marimo.py.tpl**

File: `src/nuv/templates/spark/explore_marimo.py.tpl`

```python
import marimo

__generated_with = "0.10.0"
app = marimo.App(width="medium")


@app.cell
def _():
    from pyspark.sql import SparkSession

    spark = SparkSession.builder.master("local[*]").appName("{name}").getOrCreate()
    spark
    return (spark,)


@app.cell
def _(spark):
    data = [("alice", 1), ("bob", 2), ("charlie", 3)]
    df = spark.createDataFrame(data, ["name", "value"])
    df.show()
    return (df,)


@app.cell
def _(df):
    filtered = df.filter(df.value > 1)
    filtered.show()
    return (filtered,)


@app.cell
def _(df):
    grouped = df.groupBy("name").sum("value")
    grouped.show()
    return (grouped,)


if __name__ == "__main__":
    app.run()
```

**Step 2: Add `generate_jupyter_notebook()` to `src/nuv/commands/new.py`**

Add this function before `scaffold_files`:

```python
import json

def generate_jupyter_notebook(name: str) -> str:
    """Build a starter Jupyter notebook as JSON.

    Generated programmatically instead of via .tpl because .ipynb JSON
    braces conflict with str.format() placeholders.
    """
    def _code_cell(source: list[str]) -> dict:
        return {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": source,
        }

    def _md_cell(source: list[str]) -> dict:
        return {
            "cell_type": "markdown",
            "metadata": {},
            "source": source,
        }

    cells = [
        _md_cell([f"# {name} — Exploration Notebook"]),
        _code_cell([
            "from pyspark.sql import SparkSession\n",
            "\n",
            f'spark = SparkSession.builder.master("local[*]").appName("{name}").getOrCreate()\n',
            "spark",
        ]),
        _md_cell(["## Create a sample DataFrame"]),
        _code_cell([
            'data = [("alice", 1), ("bob", 2), ("charlie", 3)]\n',
            'df = spark.createDataFrame(data, ["name", "value"])\n',
            "df.show()",
        ]),
        _md_cell(["## Filter"]),
        _code_cell([
            "filtered = df.filter(df.value > 1)\n",
            "filtered.show()",
        ]),
        _md_cell(["## Group By"]),
        _code_cell([
            'grouped = df.groupBy("name").sum("value")\n',
            "grouped.show()",
        ]),
    ]

    notebook = {
        "cells": cells,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3",
            },
            "language_info": {
                "name": "python",
                "version": "3.13.0",
            },
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    return json.dumps(notebook, indent=1) + "\n"
```

**Step 3: Write a failing test for `generate_jupyter_notebook`**

Add to `tests/test_new.py`:

```python
from nuv.commands.new import generate_jupyter_notebook

def test_generate_jupyter_notebook_valid_json() -> None:
    import json
    result = generate_jupyter_notebook("my-spark-app")
    notebook = json.loads(result)
    assert notebook["nbformat"] == 4
    assert len(notebook["cells"]) == 7
    assert notebook["cells"][0]["cell_type"] == "markdown"
    assert "my-spark-app" in notebook["cells"][0]["source"][0]


def test_generate_jupyter_notebook_contains_spark_session() -> None:
    result = generate_jupyter_notebook("my-spark-app")
    assert "SparkSession" in result
    assert "my-spark-app" in result
```

**Step 4: Run tests to verify they fail**

```bash
uv run pytest tests/test_new.py::test_generate_jupyter_notebook_valid_json -v
uv run pytest tests/test_new.py::test_generate_jupyter_notebook_contains_spark_session -v
```

Expected: FAIL with `ImportError: cannot import name 'generate_jupyter_notebook'`

**Step 5: Implement `generate_jupyter_notebook` (code from Step 2)**

Add `import json` at the top of `src/nuv/commands/new.py` and the function from Step 2 before `scaffold_files`.

**Step 6: Run tests to verify they pass**

```bash
uv run pytest tests/test_new.py::test_generate_jupyter_notebook_valid_json tests/test_new.py::test_generate_jupyter_notebook_contains_spark_session -v
```

Expected: PASS

**Step 7: Commit**

```bash
git add src/nuv/templates/spark/explore_marimo.py.tpl src/nuv/commands/new.py tests/test_new.py
git commit -m "feat(spark): add notebook templates and Jupyter notebook generator"
```

---

### Task 12: Archetype-Aware Default Python Version

**Files:**
- Modify: `src/nuv/commands/new.py` (add `DEFAULT_PYTHON_VERSIONS` dict, update `run_new` signature)
- Modify: `src/nuv/cli.py` (change `--python-version` default to `None`, update help text)
- Modify: `tests/test_new.py`

Currently `DEFAULT_PYTHON_VERSION = "3.14"` is used everywhere. We need spark to default to `3.13`.

**Step 1: Write failing tests**

Add to `tests/test_new.py`:

```python
from nuv.commands.new import DEFAULT_PYTHON_VERSIONS

def test_default_python_versions_script() -> None:
    assert DEFAULT_PYTHON_VERSIONS["script"] == "3.14"


def test_default_python_versions_spark() -> None:
    assert DEFAULT_PYTHON_VERSIONS["spark"] == "3.13"


def test_run_new_spark_uses_default_python_313(tmp_path: Path) -> None:
    with (
        patch("nuv.commands.new.shutil.which", return_value="/usr/bin/uv"),
        patch("nuv.commands.new.subprocess.run") as mock_run,
    ):
        mock_run.return_value = MagicMock(returncode=0)
        result = run_new("my-spark-app", at=str(tmp_path / "my-spark-app"), cwd=tmp_path, archetype="spark")
    assert result == 0
    assert (tmp_path / "my-spark-app" / ".python-version").read_text().strip() == "3.13"
```

**Step 2: Run tests to verify they fail**

```bash
uv run pytest tests/test_new.py::test_default_python_versions_script tests/test_new.py::test_default_python_versions_spark tests/test_new.py::test_run_new_spark_uses_default_python_313 -v
```

Expected: FAIL

**Step 3: Implement**

In `src/nuv/commands/new.py`:

1. Add `DEFAULT_PYTHON_VERSIONS` dict:
   ```python
   DEFAULT_PYTHON_VERSIONS = {"script": "3.14", "spark": "3.13"}
   ```
   (Keep `DEFAULT_PYTHON_VERSION = "3.14"` for backward compat — it's imported by cli.py.)

2. Update `run_new` signature — change `python_version: str = DEFAULT_PYTHON_VERSION` to `python_version: str | None = None`, and resolve inside:
   ```python
   if python_version is None:
       python_version = DEFAULT_PYTHON_VERSIONS.get(archetype, DEFAULT_PYTHON_VERSION)
   ```

In `src/nuv/cli.py`:

1. Import `DEFAULT_PYTHON_VERSIONS` alongside existing import.
2. Change `--python-version` default from `DEFAULT_PYTHON_VERSION` to `None`.
3. Update help text: `"Python version (default: depends on archetype — script=3.14, spark=3.13)."`

**Step 4: Run tests to verify they pass**

```bash
uv run pytest tests/test_new.py::test_default_python_versions_script tests/test_new.py::test_default_python_versions_spark tests/test_new.py::test_run_new_spark_uses_default_python_313 -v
```

Expected: PASS

**Step 5: Verify existing tests still pass**

```bash
uv run pytest tests/test_new.py -v
```

Expected: ALL PASS (existing tests that pass `python_version="3.13"` explicitly still work; tests that rely on the default now get `None` from CLI but `run_new` resolves it to `"3.14"` for script archetype)

**Important:** Some existing tests call `run_new` without `python_version` and expect `3.14`. Since `run_new`'s default changes to `None`, it now resolves via `DEFAULT_PYTHON_VERSIONS["script"]` which is still `"3.14"`, so they should still pass. Tests that call `scaffold_files` directly with no `python_version` still get `DEFAULT_PYTHON_VERSION` as the keyword default — verify this works.

Actually, `scaffold_files` has its own default `python_version: str = DEFAULT_PYTHON_VERSION`. This should stay unchanged since `scaffold_files` is called by `run_new` which always passes an explicit value. But tests that call `scaffold_files` directly without `python_version` will still get `"3.14"`. No changes needed to `scaffold_files` signature.

**Step 6: Commit**

```bash
git add src/nuv/commands/new.py src/nuv/cli.py tests/test_new.py
git commit -m "feat(spark): archetype-aware default Python version (script=3.14, spark=3.13)"
```

---

### Task 13: Archetype-Aware scaffold_files + CLI Choice

This is the core integration task. `scaffold_files` needs to create different directory structures for script vs spark, and the CLI needs to accept `"spark"`.

**Files:**
- Modify: `src/nuv/commands/new.py:64-89` (`scaffold_files`)
- Modify: `src/nuv/cli.py:34` (archetype choices)
- Modify: `tests/test_new.py`

**Step 1: Write failing tests for spark scaffold**

Add to `tests/test_new.py`:

```python
def test_scaffold_files_spark_creates_expected_files(tmp_path: Path) -> None:
    target = tmp_path / "my-spark-app"
    target.mkdir()
    scaffold_files(target, name="my-spark-app", module_name="my_spark_app", archetype="spark", python_version="3.13")

    assert (target / ".python-version").exists()
    assert (target / ".gitignore").exists()
    assert (target / "main.py").exists()
    assert (target / "pyproject.toml").exists()
    assert (target / "README.md").exists()
    assert (target / "src" / "my_spark_app" / "__init__.py").exists()
    assert (target / "src" / "my_spark_app" / "_logging.py").exists()
    assert (target / "src" / "my_spark_app" / "config.py").exists()
    assert (target / "src" / "my_spark_app" / "session.py").exists()
    assert (target / "src" / "my_spark_app" / "jobs" / "__init__.py").exists()
    assert (target / "src" / "my_spark_app" / "jobs" / "example.py").exists()
    assert (target / "tests" / "__init__.py").exists()
    assert (target / "tests" / "conftest.py").exists()
    assert (target / "tests" / "test_example.py").exists()
    assert (target / "notebooks" / "explore.ipynb").exists()
    assert (target / "notebooks" / "explore_marimo.py").exists()


def test_scaffold_files_spark_python_version_content(tmp_path: Path) -> None:
    target = tmp_path / "my-spark-app"
    target.mkdir()
    scaffold_files(target, name="my-spark-app", module_name="my_spark_app", archetype="spark", python_version="3.13")
    assert (target / ".python-version").read_text().strip() == "3.13"


def test_scaffold_files_spark_pyproject_has_pyspark(tmp_path: Path) -> None:
    target = tmp_path / "my-spark-app"
    target.mkdir()
    scaffold_files(target, name="my-spark-app", module_name="my_spark_app", archetype="spark", python_version="3.13")
    pyproject = (target / "pyproject.toml").read_text()
    assert "pyspark>=4,<5" in pyproject
    assert "chispa>=0.11" in pyproject
    assert "jupyterlab>=4" in pyproject
    assert "marimo>=0.10" in pyproject
    assert "py313" in pyproject


def test_scaffold_files_spark_gitignore_has_spark_entries(tmp_path: Path) -> None:
    target = tmp_path / "my-spark-app"
    target.mkdir()
    scaffold_files(target, name="my-spark-app", module_name="my_spark_app", archetype="spark", python_version="3.13")
    content = (target / ".gitignore").read_text()
    assert "derby.log" in content
    assert "metastore_db/" in content
    assert "spark-warehouse/" in content
    assert ".ipynb_checkpoints/" in content


def test_scaffold_files_spark_main_imports_package(tmp_path: Path) -> None:
    target = tmp_path / "my-spark-app"
    target.mkdir()
    scaffold_files(target, name="my-spark-app", module_name="my_spark_app", archetype="spark", python_version="3.13")
    main_content = (target / "main.py").read_text()
    assert "from my_spark_app._logging import configure" in main_content
    assert "from my_spark_app.config import resolve_params" in main_content
    assert "from my_spark_app.session import create_spark_session" in main_content


def test_scaffold_files_spark_test_uses_chispa(tmp_path: Path) -> None:
    target = tmp_path / "my-spark-app"
    target.mkdir()
    scaffold_files(target, name="my-spark-app", module_name="my_spark_app", archetype="spark", python_version="3.13")
    test_content = (target / "tests" / "test_example.py").read_text()
    assert "from chispa import assert_df_equality" in test_content
    assert "from my_spark_app.jobs.example import transform" in test_content


def test_scaffold_files_spark_notebook_valid_json(tmp_path: Path) -> None:
    import json
    target = tmp_path / "my-spark-app"
    target.mkdir()
    scaffold_files(target, name="my-spark-app", module_name="my_spark_app", archetype="spark", python_version="3.13")
    notebook = json.loads((target / "notebooks" / "explore.ipynb").read_text())
    assert notebook["nbformat"] == 4
    assert "SparkSession" in str(notebook["cells"])


def test_scaffold_files_spark_end_with_trailing_newline(tmp_path: Path) -> None:
    target = tmp_path / "my-spark-app"
    target.mkdir()
    scaffold_files(target, name="my-spark-app", module_name="my_spark_app", archetype="spark", python_version="3.13")

    generated_files = [
        ".python-version",
        ".gitignore",
        "main.py",
        "pyproject.toml",
        "README.md",
        "src/my_spark_app/__init__.py",
        "src/my_spark_app/_logging.py",
        "src/my_spark_app/config.py",
        "src/my_spark_app/session.py",
        "src/my_spark_app/jobs/__init__.py",
        "src/my_spark_app/jobs/example.py",
        "tests/__init__.py",
        "tests/conftest.py",
        "tests/test_example.py",
        "notebooks/explore.ipynb",
        "notebooks/explore_marimo.py",
    ]

    for rel_path in generated_files:
        content = (target / rel_path).read_text()
        assert content.endswith("\n"), f"Expected trailing newline in {rel_path}"
```

**Step 2: Run tests to verify they fail**

```bash
uv run pytest tests/test_new.py -k "spark" -v
```

Expected: FAIL (scaffold_files doesn't handle spark archetype yet)

**Step 3: Implement archetype-aware scaffold_files**

Refactor `scaffold_files` in `src/nuv/commands/new.py:64-89`. Replace the current function body with archetype dispatch:

```python
def scaffold_files(
    target: Path,
    *,
    name: str,
    module_name: str,
    archetype: str = "script",
    python_version: str = DEFAULT_PYTHON_VERSION,
) -> None:
    validate_python_version(python_version)
    template_vars = {
        "name": name,
        "module_name": module_name,
        "archetype": archetype,
        "python_version": python_version,
    }

    write_with_trailing_newline(target / ".python-version", python_version)
    write_with_trailing_newline(target / ".gitignore", render_template("gitignore.tpl", **template_vars))
    write_with_trailing_newline(target / "pyproject.toml", render_template("pyproject.toml.tpl", **template_vars))
    write_with_trailing_newline(target / "README.md", render_template("readme.md.tpl", **template_vars))
    write_with_trailing_newline(target / "main.py", render_template("main.py.tpl", **template_vars))

    tests_dir = target / "tests"
    tests_dir.mkdir()
    write_with_trailing_newline(tests_dir / "__init__.py", "")

    if archetype == "script":
        write_with_trailing_newline(target / "_logging.py", render_template("_logging.py.tpl", **template_vars))
        write_with_trailing_newline(tests_dir / "test_main.py", render_template("test_main.py.tpl", **template_vars))
    elif archetype == "spark":
        _scaffold_spark(target, template_vars=template_vars, name=name, module_name=module_name)


def _scaffold_spark(
    target: Path,
    *,
    template_vars: dict[str, str],
    name: str,
    module_name: str,
) -> None:
    # src/<module_name>/ package
    pkg_dir = target / "src" / module_name
    pkg_dir.mkdir(parents=True)
    write_with_trailing_newline(pkg_dir / "__init__.py", render_template("init.py.tpl", **template_vars))
    write_with_trailing_newline(pkg_dir / "_logging.py", render_template("_logging.py.tpl", **template_vars))
    write_with_trailing_newline(pkg_dir / "config.py", render_template("config.py.tpl", **template_vars))
    write_with_trailing_newline(pkg_dir / "session.py", render_template("session.py.tpl", **template_vars))

    # src/<module_name>/jobs/
    jobs_dir = pkg_dir / "jobs"
    jobs_dir.mkdir()
    write_with_trailing_newline(jobs_dir / "__init__.py", render_template("jobs_init.py.tpl", **template_vars))
    write_with_trailing_newline(jobs_dir / "example.py", render_template("example_job.py.tpl", **template_vars))

    # tests/
    tests_dir = target / "tests"
    write_with_trailing_newline(tests_dir / "conftest.py", render_template("conftest.py.tpl", **template_vars))
    write_with_trailing_newline(tests_dir / "test_example.py", render_template("test_example.py.tpl", **template_vars))

    # notebooks/
    notebooks_dir = target / "notebooks"
    notebooks_dir.mkdir()
    write_with_trailing_newline(notebooks_dir / "explore.ipynb", generate_jupyter_notebook(name))
    write_with_trailing_newline(notebooks_dir / "explore_marimo.py", render_template("explore_marimo.py.tpl", **template_vars))
```

**Step 4: Run spark tests to verify they pass**

```bash
uv run pytest tests/test_new.py -k "spark" -v
```

Expected: ALL PASS

**Step 5: Run ALL tests to verify nothing is broken**

```bash
uv run pytest tests/test_new.py -v
```

Expected: ALL PASS (existing script tests unchanged)

**Step 6: Add "spark" to CLI archetype choices**

In `src/nuv/cli.py:34`, change:
```python
choices=["script"],
```
to:
```python
choices=["script", "spark"],
```

**Step 7: Write CLI test for spark archetype**

Add to `tests/test_new.py`:

```python
def test_cli_new_spark_archetype(tmp_path: Path) -> None:
    with (
        patch("nuv.commands.new.shutil.which", return_value="/usr/bin/uv"),
        patch("nuv.commands.new.subprocess.run") as mock_run,
    ):
        mock_run.return_value = MagicMock(returncode=0)
        result = cli_main(["new", "my-spark-app", "--at", str(tmp_path / "my-spark-app"), "--archetype", "spark"])
    assert result == 0
    assert (tmp_path / "my-spark-app" / "src" / "my_spark_app" / "__init__.py").exists()
    assert (tmp_path / "my-spark-app" / "notebooks" / "explore.ipynb").exists()


def test_cli_spark_default_python_version(tmp_path: Path) -> None:
    with (
        patch("nuv.commands.new.shutil.which", return_value="/usr/bin/uv"),
        patch("nuv.commands.new.subprocess.run") as mock_run,
    ):
        mock_run.return_value = MagicMock(returncode=0)
        result = cli_main(["new", "my-spark-app", "--at", str(tmp_path / "my-spark-app"), "--archetype", "spark"])
    assert result == 0
    assert (tmp_path / "my-spark-app" / ".python-version").read_text().strip() == "3.13"
```

**Step 8: Run ALL tests**

```bash
uv run pytest tests/test_new.py -v
```

Expected: ALL PASS

**Step 9: Run linter and formatter**

```bash
uv run ruff check src/ tests/
uv run ruff format --check src/ tests/
```

Expected: No errors

**Step 10: Commit**

```bash
git add src/nuv/commands/new.py src/nuv/cli.py tests/test_new.py
git commit -m "feat(spark): archetype-aware scaffold_files and CLI spark choice"
```

---

### Task 14: Full Integration Tests

**Files:**
- Modify: `tests/test_new.py`

**Step 1: Write integration tests**

Add to `tests/test_new.py`:

```python
def test_run_new_spark_success(tmp_path: Path) -> None:
    with (
        patch("nuv.commands.new.shutil.which", return_value="/usr/bin/uv"),
        patch("nuv.commands.new.subprocess.run") as mock_run,
    ):
        mock_run.return_value = MagicMock(returncode=0)
        result = run_new("my-spark-app", at=str(tmp_path / "my-spark-app"), cwd=tmp_path, archetype="spark")
    assert result == 0
    assert (tmp_path / "my-spark-app" / "main.py").exists()
    assert (tmp_path / "my-spark-app" / "src" / "my_spark_app" / "config.py").exists()
    assert (tmp_path / "my-spark-app" / "notebooks" / "explore.ipynb").exists()


def test_run_new_spark_cleanup_on_failure(tmp_path: Path) -> None:
    with patch("nuv.commands.new.shutil.which", return_value=None):
        result = run_new("my-spark-app", cwd=tmp_path, archetype="spark")
    assert result == 1
    assert not (tmp_path / "my-spark-app").exists()


def test_run_new_spark_keep_on_failure(tmp_path: Path) -> None:
    with patch("nuv.commands.new.shutil.which", return_value=None):
        result = run_new("my-spark-app", cwd=tmp_path, archetype="spark", keep_on_failure=True)
    assert result == 1
    assert (tmp_path / "my-spark-app").exists()
```

**Step 2: Run them**

```bash
uv run pytest tests/test_new.py -k "run_new_spark" -v
```

Expected: ALL PASS

**Step 3: Run full test suite with coverage**

```bash
uv run pytest tests/test_new.py --cov=nuv --cov-report=term-missing --cov-fail-under=100
```

Expected: ALL PASS, 100% coverage. If coverage drops, add tests for any uncovered lines.

**Step 4: Commit**

```bash
git add tests/test_new.py
git commit -m "test(spark): add integration tests for spark archetype"
```

---

### Task 15: Update CI Smoke Test

**Files:**
- Modify: `.github/workflows/ci.yml`

**Step 1: Add spark smoke test to CI**

In `.github/workflows/ci.yml`, after the existing integration smoke test step, add a parallel spark smoke test. Note: this smoke test will only work if the CI runner has Java installed (required by PySpark). Ubuntu runners include Java by default.

Add after the existing `Integration smoke test` step (around line 57):

```yaml
      - name: Integration smoke test (spark)
        if: matrix.python-version == '3.14'
        run: |
          uv run --frozen nuv new spark-smoke --at /tmp/spark-smoke --archetype spark --python-version 3.13
          cd /tmp/spark-smoke && uv sync --frozen && uv run --frozen pytest
```

**Step 2: Commit**

```bash
git add .github/workflows/ci.yml
git commit -m "ci: add spark archetype integration smoke test"
```

---

### Task 16: Final Verification

**Step 1: Run full test suite**

```bash
uv run pytest --cov=nuv --cov-report=term-missing --cov-fail-under=100
```

Expected: ALL PASS, 100% coverage

**Step 2: Run linter + formatter**

```bash
uv run ruff check src/ tests/
uv run ruff format --check src/ tests/
```

Expected: Clean

**Step 3: Manual smoke test**

```bash
uv run nuv new my-spark-app --archetype spark --at /tmp/my-spark-app
cd /tmp/my-spark-app
uv sync
uv run pytest
uv run python main.py --help
uv run python main.py --env dev --job example
```

Expected: Project generates, syncs, tests pass, CLI works. If Java is not installed, PySpark will fail at runtime — that's expected on machines without JDK. The structural test (files exist, templates rendered) verifies correctness.

**Step 4: Clean up smoke test**

```bash
rm -rf /tmp/my-spark-app
```
