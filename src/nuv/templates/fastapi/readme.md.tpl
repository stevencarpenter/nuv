# {name}

## Setup

```bash
uv sync
```

## Usage

```bash
uv run python main.py --help
uv run python main.py --host 0.0.0.0 --port 8000
```

## Development

```bash
uv run pytest          # run tests
uv run ruff check .    # lint
uv run ruff format .   # format
uv run ty check .      # type check
```

## Docker

```bash
docker build -t {name} .
docker run -p 8000:8000 {name}
```

The default container bind address is `0.0.0.0` so Docker can publish the service. Use container networking, a reverse proxy, or firewall rules to control production exposure.
