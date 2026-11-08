# {name}

<!-- One line: what this does, and when someone should run it. -->

Scaffolded by [nuv](https://github.com/stevencarpenter/nuv) (`util` archetype).

## Usage

```bash
uv run {name} --help
uv run {name} --dry-run       # rehearse: report what would change, change nothing
```

From another directory (keeps your current working directory):

```bash
uv run --project path/to/{name} {name} --help
```

Put it on your PATH:

```bash
uv tool install --editable .
```

## Development

```bash
uv run pytest                 # test
uv run ruff check .           # lint
uv run ruff format .          # format
uv run ty check               # type check
uv build                      # wheel + sdist via uv_build
```
