# Architecture: nuv

## The pipeline

`cli.py` (click, thin) → `commands/new.py` (all logic) → `templates/<archetype>/*.tpl`

- `cli.py` parses, validates, and delegates. Nothing else. New behaviour belongs
  in `commands/new.py`, not in a click callback.
- `run_new()` is the single orchestrator: validate name → resolve target →
  `mkdir` → `scaffold_files()` → `uv sync` → optional tool install.
- `scaffold_files()` writes the five shared files (`.python-version`,
  `.gitignore`, `pyproject.toml`, `README.md`, `main.py`) plus `tests/`, then
  dispatches to one `_scaffold_<archetype>()` helper.

## Template contract

- Templates load from the **filesystem** —
  `_TEMPLATES_ROOT = Path(__file__).parent.parent / "templates"` — not
  `importlib.resources`. An `__init__.py` in a template directory is neither
  required nor sufficient; whether a template ships depends entirely on the
  wheel include glob `src/nuv/**/*.tpl` in `[tool.hatch.build.targets.wheel]`.
- Rendering is `str.format()`. Exactly six placeholders exist:
  `{name}`, `{module_name}`, `{python_version}`, `{python_version_nodot}`,
  `{uv_docker_image}`, `{python_docker_image}`.
  Any other `{...}` raises `KeyError`, and every literal brace must be doubled
  as `{{` / `}}`. **Neither failure is caught by ruff, ty, or any unit test that
  does not actually render that template** — they surface only when the
  archetype is scaffolded for real.
- Never add a `.ipynb.tpl`. Notebook JSON braces collide with `str.format()`;
  notebooks are built programmatically through `_notebook_json()` via
  `generate_jupyter_notebook()` / `generate_ds_notebook()`. Extend those.
- `render_template()` rejects absolute paths and `..` in both the archetype and
  the template name, then re-checks containment after `resolve()`. This is a
  path-traversal guard. Do not weaken, shortcut, or route around it.

## Error contract

`run_new()` catches exactly `ValueError`, `RuntimeError`, and `OSError`. On
those it logs at ERROR, returns exit code 1, and `shutil.rmtree`s a target
directory it created unless `--keep-on-failure` was passed.

- Raise only those three from scaffold code. Anything else escapes to `cli.py`,
  which prints `ERROR unexpected failure` and raises `SystemExit(1)` — leaving
  the half-written project directory on disk.
- Convention: invalid input → `ValueError`; missing template →
  `FileNotFoundError`; failed subprocess or missing tool → `RuntimeError`.
  `FileNotFoundError` is handled only because it subclasses `OSError` — that
  inheritance is load-bearing. A new error type that sits outside these three
  branches escapes the cleanup path.
- Partial scaffolds must never survive a failure. If new code creates state
  outside the target directory, it is responsible for its own cleanup.

## Landmines

**The archetype list is duplicated, and nothing tests that the copies agree:**

- `ARCHETYPES` in `src/nuv/cli.py` — drives the `--archetype` click choices.
- `VALID_ARCHETYPES` in `src/nuv/commands/new.py` — drives the runtime guard.
- `DEFAULT_PYTHON_VERSIONS` in `commands/new.py` — a missing entry silently
  falls back to 3.14 rather than failing.

**`scaffold_files()` has a catch-all `match` arm.** `case _:` routes to
`_scaffold_fastapi`, so an archetype added to `VALID_ARCHETYPES` without its own
explicit `case` is silently handed to the FastAPI scaffolder. Observed
behaviour: the five shared files get written, then rendering dies with
`FileNotFoundError: Template not found: <archetype>/init.py.tpl` — an error
naming a FastAPI-layout template nobody wrote, which reads as a missing-file bug
rather than a missing dispatch arm. An archetype that happens to define
FastAPI's filenames (`init.py.tpl`, `config.py.tpl`, `conftest.py.tpl`, …) gets
further before failing, or emits a FastAPI-shaped project outright. Always add
the arm.

**Docker images are SHA-pinned by Python version.** `UV_DOCKER_IMAGES` and
`PYTHON_DOCKER_IMAGES` map `3.13`/`3.14` to digest-pinned references; a version
absent from those maps falls back to an **unpinned** tag. Supporting a new
Python version means adding both digests.

## Name handling

`validate_name()` is the only place a project name is sanitized: it enforces the
character set, rejects leading/trailing punctuation, and confirms that
`name.replace("-", "_")` is a valid, non-keyword, non-soft-keyword Python
identifier. `module_name` is always derived that way — never re-derive it
ad hoc elsewhere.
