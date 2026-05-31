# {name}

A data science project scaffolded by [nuv](https://github.com/stevencarpenter/nuv).

## Manifesto: all of what you need or want, but off by default

`pyproject.toml` ships a thin active core — numpy, pandas, Arrow, a CLI, and
typed config — alongside a curated, commented catalog of the rest of the
modern stack: classical ML, deep learning, neural nets, LLMs, experiment
tracking, and visualization. Uncomment a line, run `uv sync`, and uv resolves
it against everything already locked. Your environment stays lean until you
decide otherwise.

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

Two notebook front-ends ship side by side — pick your flavor.

```bash
# Jupyter / IPython
uv run jupyter lab notebooks/

# marimo (reactive, git-friendly .py notebooks)
uv run marimo edit notebooks/explore_marimo.py
```

## Layout

```
{name}/
├── main.py                       # Click CLI entry point
├── pyproject.toml                # thin core + commented catalog
├── src/{module_name}/
│   ├── _logging.py
│   ├── config.py                 # Pydantic settings (paths, seed, ...)
│   └── data.py                   # CSV/Parquet/JSON I/O + quick-look helpers
├── tests/
│   ├── conftest.py
│   └── test_data.py
├── notebooks/
│   ├── explore.ipynb             # Jupyter / IPython
│   └── explore_marimo.py         # marimo
├── data/
│   ├── raw/                      # inputs (gitignored)
│   └── processed/                # derived data (gitignored)
└── models/                       # trained artifacts (gitignored)
```
