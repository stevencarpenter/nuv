# Copilot Instructions

## Project overview

`nuv` is a CLI tool that scaffolds opinionated uv-based Python projects. Running `nuv new <name>` creates a fully configured project with argparse, logging, 100% test coverage, ruff linting/formatting, and ty type checking — all green from commit zero.

## Tech stack

- **Language:** Python 3.14+
- **Package manager:** [uv](https://docs.astral.sh/uv/)
- **Testing:** pytest with 100% branch coverage enforced (`pytest-cov`)
- **Linting/formatting:** [ruff](https://docs.astral.sh/ruff/)
- **Type checking:** [ty](https://github.com/astral-sh/ty)

## Repository layout

```
src/nuv/
  cli.py            # argparse entry point; routes subcommands
  commands/
    new.py          # logic for `nuv new`: validate, scaffold, uv sync
  templates/
    script/         # *.tpl files rendered via string.Template
tests/
  test_new.py       # unit tests (100% coverage required)
```

## Development commands

```bash
# Install dev dependencies
uv sync

# Run all tests (with coverage)
uv run pytest

# Lint
uv run ruff check src/ tests/

# Format check
uv run ruff format --check src/ tests/

# Type check
uv run ty check src/
```

## Coding conventions

- All source lives under `src/nuv/`; tests live under `tests/`.
- 100% branch coverage is enforced — every new code path must have a corresponding test.
- Use `string.Template` (not f-strings or Jinja) for file templates stored in `src/nuv/templates/`.
- Public functions are typed with PEP 604 union syntax (`X | None`) and return types annotated.
- Errors are surfaced by raising `ValueError` or `RuntimeError`; callers catch and print to stderr, returning exit code 1.
- Do not introduce new runtime dependencies without updating `pyproject.toml` and `uv.lock`.
- Follow ruff lint rules: `E`, `F`, `I`, `UP`, `B`, `SIM`.

## Adding a new archetype

1. Create `src/nuv/templates/<archetype>/` with the required `.tpl` files (see `script/` as a reference).
2. Add any new logic to `src/nuv/commands/`.
3. Wire the archetype in `cli.py` if needed.
4. Add tests to maintain 100% coverage.
