# {name}

A reusable utility scaffolded by [nuv](https://github.com/stevencarpenter/nuv) (`util` archetype).
Lean on purpose: click plus the stdlib, built with `uv_build`, checked by ruff, ty, and pytest.

## Commands

```bash
uv run {name} --help          # run the tool
uv run {name} --dry-run       # rehearse without side effects
uv add <package>              # add a runtime dependency (uv only, never pip)
uv add --dev <package>        # add a dev-only dependency
```

## Definition of done

All four pass before the tool is handed over:

```bash
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run ty check
```

## Where things go

- `src/{module_name}/main.py`: `run()` holds the logic. `_cli` and `main()` only parse options and call it, so `run()` stays importable and testable.
- When `main.py` stops being easy to read, split it into more modules under `src/{module_name}/`. Do not add a root-level `main.py`.
- `tests/`: test `run()` directly for logic, and `main([...])` for option parsing and exit codes.
- Keep the README's Usage section current, so the next person (or agent) can run the tool cold.

## Conventions

- Log progress and diagnostics instead of printing: one `log = logging.getLogger(__name__)` per module, and `configure()` is called once, in `_cli`. Keep stdout for the tool's actual output.
- Exit codes: return non-zero from `run()` to signal a finding (for example, drift detected). `raise click.ClickException("why")` for a clean failure (exit 1). Usage errors exit 2.
- Annotate public functions. Use `X | None`, not `Optional[X]`.
- Take config and secrets from options or environment variables. Never hard-code them.

## Tools that change things (migrations, remediations, backfills)

- Thread `dry_run` through every side effect, and log each change as `would ...` or `did ...`.
- Make reruns safe: check the current state before changing it, so a second run is a no-op.
- For anything destructive or hard to undo, flip the default: dry run unless `--apply` is passed.
- Log a summary at the end: how many items were checked, changed, and skipped.
- If the tool never changes anything, delete `--dry-run`.
