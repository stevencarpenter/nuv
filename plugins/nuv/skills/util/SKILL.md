---
name: util
description: Give any Python script a pinned environment with uv instead of writing a loose .py file. Use when you are about to write or hand over Python code outside an existing project, whether a one-off check, a helper you will call again, a data or schema migration, a remediation, cleanup, or backfill, or an ops or reporting task, or when a throwaway script is turning into one of those.
---

# Python scripts get a pinned environment, never a loose `.py`

A loose `fix_things.py` has no pinned dependencies, no Python version, and no obvious way to run it again. uv fixes all three without a venv, pyenv, or a global pip install. Pick the smallest tier that fits, and move up when the script grows.

| Tier | Use when | How |
| --- | --- | --- |
| 1. Inline | You will run it exactly once, to inspect something | `uv run --with <pkg> python -c '...'`, no file left behind |
| 2. Script | One reusable file, no tests needed, read-only or low stakes | PEP 723 header, run with `uv run --script` |
| 3. Project | It needs tests or a second module, or it changes real systems (migration, remediation, backfill) | `nuv new --archetype util` |

Never `pip install`, never a bare `python script.py`, never a hand-made venv.

## Tier 2: PEP 723 script

One file that carries its own Python version and dependencies.

1. **Name** it in kebab-case, verb first: `check-orphans.py`, `export-report.py`.
2. **Place** it at the path the user gave. Otherwise, if it operates on the current repo, use `tools/<name>.py` at the repo root. Otherwise, ask.
3. **Create** it with a header, or let uv write one:

   ```bash
   uv init --script tools/<name>.py --python 3.14
   uv add --script tools/<name>.py click     # adds a pinned lower bound to the header
   ```

   ```python
   #!/usr/bin/env -S uv run --script
   # /// script
   # requires-python = ">=3.14"
   # dependencies = [
   #     "click>=8.5.0",
   # ]
   # ///
   ```

   Set `requires-python` to what the script needs. `uv add --script` writes the interpreter it happened to use.
4. **Run** it with `uv run --script tools/<name>.py`. The `--script` flag keeps a nearby `pyproject.toml` from capturing it. `chmod +x` lets the user run it directly through the shebang.
5. **Hand off** with the exact invocation. For a run the user must reproduce later, `uv lock --script tools/<name>.py` writes `<name>.py.lock` beside it.

Move to tier 3 when the file needs a test, a second module, or starts changing external state. Its body becomes `run()`.

## Tier 3: `util` project

A uv project with a console script, the `uv_build` backend, ruff, ty, and pytest, all green before you write a line.

### Bootstrap

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

### Build

- Put the logic in `run()` in `src/<module>/main.py`, and options on `_cli`. Add modules beside `main.py` as it grows.
- Add dependencies with `uv add <pkg>` from inside the project. Never pip.
- For anything that changes external state, thread `--dry-run` through every side effect, make reruns no-ops, and rehearse with `--dry-run` before the real run.
- Write tests for the logic in `tests/` as you go.

### Done means green

From the project directory:

```bash
uv run pytest && uv run ruff check . && uv run ruff format --check . && uv run ty check
```

Then update the README's Usage section with the real invocation.

### Hand off

Tell the user where the tool lives and how to run it:

```bash
uv run --project <path> <name> --help     # from anywhere, without installing
uv tool install --editable <path>         # or put it on PATH
```

Only install it on their PATH if they ask.
