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