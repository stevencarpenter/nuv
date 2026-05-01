# Polars + DuckDB + Delta Local Data Lake Archetype

## Overview

A new `polars` archetype for `nuv new` that scaffolds an opinionated local data lake project using Polars, DuckDB, and Delta Lake. Designed for the workflow: pull down GBs of data locally, operate on it with modern tooling, iterate fast.

## Tech Stack

| Layer | Choice | Why |
|---|---|---|
| Data transforms | Polars | Fast expression API, lazy execution, Rust-native |
| SQL analytics | DuckDB | In-process OLAP, Delta extension, Polars interop |
| Storage format | Delta Lake | ACID, schema enforcement, time travel, open format |
| Notebooks | marimo | Reactive, reproducible, no separate server |
| Config | pydantic-settings | Typed settings from env/.env |
| CLI | click | Modern, composable, nested commands |
| Packaging | uv | Lockfile, fast resolution, single tool |
| Indentation | spaces | No tabs anywhere |

## Project Structure

```
{name}/
├── src/{module_name}/
│   ├── __init__.py
│   ├── _logging.py
│   ├── _io.py
│   ├── _db.py
│   ├── config.py
│   └── main.py
├── data/
│   ├── raw/
│   ├── features/
│   └── warehouse.db
├── notebooks/
│   └── explore.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   └── test_io.py
├── pyproject.toml
└── .gitignore
```

## Generated Modules

### `_io.py` — Standard Read/Write/Display Library

Thin wrappers over Polars, under 100 lines. Every project starts with the same vocabulary. User deletes or modifies freely.

```
read_csv(path, **kwargs) -> pl.DataFrame
read_parquet(path, **kwargs) -> pl.DataFrame
read_delta(path, **kwargs) -> pl.DataFrame
read_json(path, **kwargs) -> pl.DataFrame

write(df, path, **kwargs) -> None           # format from extension
write_delta(df, path, mode="overwrite")     # explicit Delta writer

show(df, max_rows=20)                       # formatted table print
glimpse(df)                                 # columns/count/dtypes summary
```

### `_db.py` — DuckDB Bridge

```
attach(path, name="lake")                   # attach a Delta directory
sql(query) -> pl.DataFrame                  # run SQL, return Polars
```

### `config.py` — Pydantic Settings

```
data_root: Path      # defaults to project_root / "data"
warehouse: Path      # defaults to data_root / "warehouse.db"
log_level: str       # defaults to "INFO"
```

### `main.py` — Click CLI

click-based entry point with `--log-level`. No predefined subcommands — open canvas. Minimal, follows same pattern as other archetypes but uses click instead of argparse.

### `_logging.py`

Same standard format module used across all archetypes. Single source of logging config.

### `notebooks/explore.py`

A marimo notebook scaffold with a default cell importing the project's modules and showing a welcome message. Ready to run with `marimo edit notebooks/explore.py`.

## Dependencies

### Runtime requirements

```
polars>=1
duckdb>=1
deltalake>=0.20
pydantic-settings>=2
click>=8
```

### Dev requirements

```
pytest>=8
pytest-cov>=6
ruff>=0.9
ty>=1
marimo>=0.11
```

### Python

`requires-python = ">=3.11"`, defaults to latest stable (3.14). No version pin constraints unlike the Spark archetype.

## Testing

### conftest.py fixtures

```
delta_path(tmp_path)       # temp directory for Delta I/O
sample_df()                # pl.DataFrame({"x": [1,2,3], "y": ["a","b","c"]})
```

Delta tables are directory-based and cheap to create in tests — no mocking needed. This is a deliberate property of the stack.

### Coverage target

90% branch coverage. Achievable on the generated code (thin wrappers). Leaves room for user-added transform logic without friction on day one.

### test_io.py

Tests for read/write round-trips through each format. Tests for show() and glimpse() display functions. Uses tmp_path fixtures.

## Nuv Template Wiring

### Archetype registration

```
# In src/nuv/commands/new.py:
VALID_ARCHETYPES = ["script", "spark", "fastapi", "polars"]
```

### Template directory

```
src/nuv/templates/polars/
  __init__.py.tpl
  _logging.py.tpl
  _io.py.tpl
  _db.py.tpl
  config.py.tpl
  main.py.tpl
  pyproject.toml.tpl
  .gitignore.tpl
  notebooks/explore.py.tpl
  tests/__init__.py.tpl
  tests/conftest.py.tpl
  tests/test_io.py.tpl
```

All `.tpl` files rendered with `str.format()` using `{name}` and `{module_name}` variables, matching existing convention.

### Scaffold function

```
_scaffold_polars(target, module_name, python_version, install_mode)
```

Follows same pattern as `_scaffold_spark` and `_scaffold_fastapi`. Copies template tree, renders files, creates `data/` subdirectories, runs `uv sync`, optionally installs with `uv tool install`.

## Future Extensions (Not In Scope)

These are deferred to separate issues:

- `--with-lancedb` flag: adds LanceDB vector store integration, wired for similarity search on feature embeddings alongside Delta tables
- `--with-ingest` flags: opinionated data source connectors (S3, Postgres, etc.)
- Extract `_io.py` module into standalone library