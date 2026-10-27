---
description: Scaffold a reusable Python utility with nuv instead of writing a loose .py file. Use when you are about to write a Python script that will run more than once or be handed to the user to run (a helper you will call again, a data or schema migration, a remediation, cleanup, or backfill, an ops or reporting task), or when a throwaway script is turning into one of those.
---

# Reusable Python utilities start from `nuv new --archetype util`

A loose `fix_things.py` has no pinned dependencies, no tests, and no obvious way to run it again. The `util` archetype is a uv project with a console script, the `uv_build` backend, ruff, ty, and pytest, all green before you write a line.

## Use it, or skip it

Use it when the script will run more than once, will be handed to someone, touches real systems (migration, remediation, backfill), or needs third-party packages.

Skip it for code you will run exactly once to inspect something. Run that inline (`uv run --with <pkg> python -c '...'`) and leave no file behind.

## 1. Bootstrap

1. **Name** it in kebab-case, verb first: `backfill-orders`, `rotate-iam-keys`, `prune-stale-branches`.
2. **Place** it at the path the user gave. Otherwise, if it operates on the current repo or its infrastructure, use `tools/<name>/` at the repo root. Otherwise, ask the user where it should live.
3. **Scaffold** it, preferring `nuv` on PATH:

   ```bash
   nuv new <name> --archetype util --at <path>
   # without nuv installed, or if this nuv rejects --archetype util as too old:
   uvx nuv@latest new <name> --archetype util --at <path>
   ```

   nuv runs `uv sync` for you. On a non-zero exit it removes what it created, so fix the cause it logs (bad name, directory already exists) and rerun.
4. **Read** `<path>/AGENTS.md`. It is the project's working agreement: layout, conventions, and the rules for tools that change things.

## 2. Build

- Put the logic in `run()` in `src/<module>/main.py`, and options on `_cli`. Add modules beside `main.py` as it grows.
- Add dependencies with `uv add <pkg>` from inside the project. Never pip.
- For anything that changes external state, thread `--dry-run` through every side effect, make reruns no-ops, and rehearse with `--dry-run` before the real run.
- Write tests for the logic in `tests/` as you go.

## 3. Done means green

From the project directory:

```bash
uv run pytest && uv run ruff check . && uv run ruff format --check . && uv run ty check
```

Then update the README's Usage section with the real invocation.

## 4. Hand off

Tell the user where the tool lives and how to run it:

```bash
uv run --project <path> <name> --help     # from anywhere, without installing
uv tool install --editable <path>         # or put it on PATH
```

Only install it on their PATH if they ask.
