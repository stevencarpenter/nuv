# Copilot Instructions

## Project overview

`nuv` is a CLI tool that scaffolds opinionated uv-based Python projects. Running `nuv new <name>` creates a fully configured project with click, logging, a passing test suite, ruff linting/formatting, and ty type checking — all green from commit zero.

## Tech stack

- **Language:** Python 3.11+ (`requires-python = ">=3.11"`). CI runs the test matrix on 3.11 and 3.14; `.python-version` pins 3.14 for local development, but that is not the support floor. Generated projects target their own per-archetype version (`DEFAULT_PYTHON_VERSIONS`) and are not bound by nuv's floor.
- **Package manager:** [uv](https://docs.astral.sh/uv/)
- **Testing:** pytest with branch coverage enforced at 92% (`--cov-fail-under=92`, `pytest-cov`)
- **Linting/formatting:** [ruff](https://docs.astral.sh/ruff/)
- **Type checking:** [ty](https://github.com/astral-sh/ty)

## Repository layout

```
src/nuv/
  _logging.py       # LOG_FORMAT + configure(); single source of logging config
  cli.py            # click entry point; routes subcommands
  commands/
    new.py          # logic for `nuv new`: validate, scaffold, uv sync
  templates/
    script/         # *.tpl files rendered via str.format()
    spark/
    fastapi/
    polars/
    ds/
tests/
  test_new.py       # unit tests (92% branch coverage gate)
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
- Branch coverage is enforced at 92% (`--cov-fail-under=92`) and currently sits near 99% — every new code path should have a corresponding test, and the gate is a floor, not a target.
- Use `str.format()` (not f-strings or Jinja) for file templates stored in `src/nuv/templates/`; placeholders use `{name}` syntax, and literal `{`/`}` must be written as `{{`/`}}`.
- Public functions are typed with PEP 604 union syntax (`X | None`) and return types annotated.
- Errors are surfaced by raising `ValueError`, `RuntimeError`, or `FileNotFoundError` (for missing templates); the CLI entry point catches these, logs them at ERROR level, and returns exit code 1.
- Logging is configured once via `_logging.configure()` (defined in `src/nuv/_logging.py`). Each module uses `log = logging.getLogger(__name__)`. The click group `cli()` in `src/nuv/cli.py` calls `configure(log_level)` from the `--log-level` option (default `WARNING`). Scaffolded projects include an identical `_logging.py` module so the pattern carries forward.
- Do not use `print()` for user-facing output — use `log.info()` for success messages and `log.error()` for errors.
- Do not introduce new runtime dependencies without updating `pyproject.toml` and `uv.lock`.
- Follow ruff lint rules: `E`, `F`, `I`, `UP`, `B`, `SIM`.

## Adding a new archetype

All eight steps are required. Use `ds` as the reference — it is the only archetype wired end to end.

1. Create `src/nuv/templates/<archetype>/` with the required `.tpl` files.
2. Add the archetype to `ARCHETYPES` in `src/nuv/cli.py` (drives the `--archetype` choices).
3. Add it to `VALID_ARCHETYPES` in `src/nuv/commands/new.py` (drives the runtime guard). These two lists are duplicated and nothing tests that they agree.
4. Add a `DEFAULT_PYTHON_VERSIONS` entry in `src/nuv/commands/new.py` — a missing entry silently falls back to 3.14 instead of failing.
5. Write a `_scaffold_<archetype>()` helper **and** an explicit `case` arm in `scaffold_files()`. The `match` ends in `case _:` routing to `_scaffold_fastapi`, so a missing arm sends your archetype to the FastAPI scaffolder — it fails with a confusing `FileNotFoundError: Template not found: <archetype>/init.py.tpl`.
6. Add tests to `tests/test_new.py`. Stub heavy runtime dependencies (see `_install_pyspark_stubs`) — nuv's own suite must never require an archetype's runtime stack.
7. Add a scaffold smoke-test step to `.github/workflows/ci.yml` that runs the generated project's `pytest`, `ruff check`, `ruff format --check`, and `ty check`.
8. Add a `### <archetype>` section under `## Archetypes` in `README.md`.

Templates render through `str.format()`, so brace mistakes and unknown placeholders fail only at scaffold time — never at lint or type-check time. Always scaffold the archetype for real before calling it done.
