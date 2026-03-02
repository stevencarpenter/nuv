# Spark Archetype Design

## Overview

Add a `spark` archetype to nuv that generates a fully configured PySpark 4 project with modular package structure, testing with chispa, dual notebook environment (Jupyter + marimo), and a parameter resolver designed for future Databricks integration.

**Usage:** `nuv new my-spark-app --archetype spark [--python-version 3.13]`

## Decisions

| Decision | Choice | Rationale |
|---|---|---|
| Project structure | src/ layout package | PySpark projects need multiple modules (jobs, config, session) |
| Notebooks | Jupyter + marimo | Jupyter for Databricks compatibility, marimo for git-friendly local dev |
| Testing | Local SparkSession + chispa | Real Spark operations with expressive DataFrame assertions |
| Entry point | argparse CLI | CLI args > env vars > defaults; simple, no Databricks coupling in phase 1 |
| Config resolution | CLI args > env vars > defaults | Clean for local dev; Databricks widgets deferred to phase 2 |
| PySpark version | 4.x (pinned >=4,<5) | Latest stable release |
| Default Python | 3.13 | Most proven with PySpark 4 + Java interop |
| Integration | New archetype choice | `--archetype spark` follows existing pattern, shares validation/scaffolding logic |
| Architecture | Minimal template set (Approach A) | Reuse existing pipeline, avoid premature abstraction |

## Generated Project Structure

```
my-spark-app/
├── .python-version              # 3.13 (configurable)
├── .gitignore                   # Extended for Spark artifacts
├── pyproject.toml               # PySpark 4, chispa, pytest, ruff, ty, hatchling
├── README.md                    # Setup, usage, test, notebook instructions
├── main.py                      # Entry point: parses args, creates SparkSession, dispatches jobs
├── src/
│   └── my_spark_app/
│       ├── __init__.py
│       ├── _logging.py          # Suppresses noisy Spark/Py4J/Java logging
│       ├── config.py            # resolve_params(): CLI args > env vars > defaults
│       ├── session.py           # create_spark_session() helper
│       └── jobs/
│           ├── __init__.py
│           └── example.py       # One example transform function
├── tests/
│   ├── __init__.py
│   ├── conftest.py              # Session-scoped SparkSession fixture
│   └── test_example.py          # chispa assert_df_equality test
└── notebooks/
    ├── explore.ipynb            # Jupyter: SparkSession + sample DataFrame ops
    └── explore_marimo.py        # marimo: same content, git-friendly format
```

## Template Details

### pyproject.toml

```toml
[project]
name = "{name}"
version = "0.1.0"
requires-python = ">={python_version}"

dependencies = [
    "pyspark>=4,<5",
]

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

[project.scripts]
{name} = "main:main"

[tool.pytest.ini_options]
addopts = "--cov={module_name} --cov-report=term-missing --cov-fail-under=100"

[tool.ruff]
target-version = "py{python_version_nodot}"
line-length = 180

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B", "SIM"]
```

### main.py — Entry Point

```python
"""Entry point for {name}."""

import sys
from {module_name}._logging import configure
from {module_name}.config import resolve_params
from {module_name}.session import create_spark_session
from {module_name}.jobs import example


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

### config.py — Parameter Resolution

```python
"""Resolve parameters from CLI args, env vars, and defaults."""

import argparse
import os

DEFAULTS = {
    "env": "dev",
    "job": "example",
    "log_level": "WARNING",
}


def resolve_params(argv: list[str] | None = None) -> dict[str, str]:
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", default=None)
    parser.add_argument("--job", default=None)
    parser.add_argument("--log-level", dest="log_level", default=None)
    parsed = parser.parse_args(argv)

    params: dict[str, str] = {}
    for key, default in DEFAULTS.items():
        cli_val = getattr(parsed, key, None)
        env_val = os.environ.get(f"SPARK_APP_{key.upper()}")
        params[key] = cli_val or env_val or default
    return params
```

### session.py — SparkSession Factory

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

### _logging.py — Noise Suppression

```python
"""Logging configuration with Spark noise suppression."""

import logging

LOG_FORMAT = "%(levelname)s %(name)s: %(message)s"


def configure(level: str) -> None:
    logging.basicConfig(format=LOG_FORMAT, level=getattr(logging, level))
    for name in ("py4j", "pyspark", "org.apache.spark"):
        logging.getLogger(name).setLevel(logging.WARNING)
```

### jobs/example.py — Example Transform

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

### tests/conftest.py — SparkSession Fixture

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

### tests/test_example.py — chispa Test

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

### .gitignore — Extended for Spark

Standard nuv gitignore plus:
```
# Spark
derby.log
metastore_db/
spark-warehouse/
*.parquet
*.snappy
.ipynb_checkpoints/
```

### Notebooks

**explore.ipynb** — Pre-populated Jupyter notebook with cells for:
1. SparkSession creation
2. Sample DataFrame creation
3. Basic operations (filter, groupBy, select)
4. Display results

**explore_marimo.py** — Same content as Jupyter notebook in marimo reactive format. Git-friendly, runnable with `marimo run notebooks/explore_marimo.py`.

## nuv Codebase Changes

### cli.py

Add `"spark"` to archetype choices. Make default Python version archetype-aware (script=3.14, spark=3.13).

### commands/new.py

Extend `scaffold_files` to be archetype-aware:
- Script: flat file list (unchanged)
- Spark: nested src/ layout with subdirectories (src/{module_name}/, src/{module_name}/jobs/, tests/, notebooks/)

Reuse existing validation, target resolution, uv sync, and install logic.

### Templates (src/nuv/templates/spark/)

```
spark/
├── __init__.py
├── config.py.tpl
├── conftest.py.tpl
├── example_job.py.tpl
├── explore.ipynb.tpl
├── explore_marimo.py.tpl
├── gitignore.tpl
├── init.py.tpl
├── jobs_init.py.tpl
├── _logging.py.tpl
├── main.py.tpl
├── pyproject.toml.tpl
├── readme.md.tpl
├── session.py.tpl
└── test_example.py.tpl
```

### Testing (nuv itself)

Mirror existing test_new.py patterns:
- Spark-specific file scaffolding (correct files in correct directories)
- Template rendering with variable substitution
- Archetype dispatch (script vs spark produces different outputs)
- Maintain 100% coverage

## Out of Scope (Phase 2+)

- Databricks widget parameter resolution
- Databricks Asset Bundles (DABs) configuration
- Cluster-aware SparkSession (detect Databricks runtime, skip `.master()`)
- Notebook sync to Databricks (`databricks sync`)
- Delta Lake / Unity Catalog integration
- Job orchestration patterns
- CI/CD templates for Databricks deployment
