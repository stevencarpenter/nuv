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
