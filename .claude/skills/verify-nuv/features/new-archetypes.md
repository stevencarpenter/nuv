# Create a project from each archetype

`nuv new <name> --archetype <archetype>` creates a project with the layout, dependencies, and
default Python version of that archetype. The archetypes are `script` (default, see
[Create a script project](./new-script.md)), `util`, `fastapi`, `polars`, `ds`, and `spark`.
Each generated project must pass its own gates and its entry point must run.

## Sub-features

- `arch-util` creates a src-layout utility with a console script, `AGENTS.md`, and `CLAUDE.md`.
- `arch-fastapi` creates a FastAPI service with a Dockerfile and a `/healthz` route.
- `arch-polars` creates a Polars, DuckDB, and Delta Lake project with `data/` directories.
- `arch-ds` creates a data science project with two notebooks and `.gitkeep` scratch directories.
- `arch-spark` creates a PySpark project with jobs and two notebooks.

## How to get to it (user POV)

- Run `nuv new <name> --archetype util`.
- Run `nuv new <name> --archetype fastapi`.
- Run `nuv new <name> --archetype polars`.
- Run `nuv new <name> --archetype ds`.
- Run `nuv new <name> --archetype spark`.

## Driving it with nuv-verify

Preconditions:

- The baseline in [README](./README.md) holds.
- The scratch directory has no `fix-thing`, `api-demo`, `pipe-demo`, `ds-demo`, or `spark-demo` entry.
- Port `18765` on `127.0.0.1` is free for `arch-fastapi`.
- Java is installed for `arch-spark`.

Every archetype uses the same four gate commands. `<dir>` is the project directory and `<id>` is
the sub-feature ID:

```bash
nv in <id>-pytest <dir> -- uv run --frozen pytest
nv in <id>-ruff   <dir> -- uv run --frozen ruff check .
nv in <id>-format <dir> -- uv run --frozen ruff format --check .
nv in <id>-ty     <dir> -- uv run --frozen ty check
```

- **util: create.** Run `nv nuv arch-util-create -- new fix-thing --archetype util`. Exit code `0`.
- **util: tree.** Run `nv tree arch-util-tree fix-thing` and `nv in arch-util-pyver fix-thing -- cat .python-version`. The tree has `AGENTS.md`, `CLAUDE.md`, `src/fix_thing/__init__.py`, `src/fix_thing/_logging.py`, `src/fix_thing/main.py`, and `tests/test_main.py`. It has no root `main.py`. The version is `3.14`.
- **util: gates.** Run the four gate commands with `arch-util` and `fix-thing`. All exit `0`, with `3 passed`.
- **util: run.** Run `nv in arch-util-run fix-thing -- uv run --frozen fix-thing --dry-run`. Exit code `0` and stderr has `fix-thing: nothing to do yet (dry run)`.
- **fastapi: create.** Run `nv nuv arch-fastapi-create -- new api-demo --archetype fastapi`. Exit code `0`.
- **fastapi: tree.** Run `nv tree arch-fastapi-tree api-demo` and `nv in arch-fastapi-pyver api-demo -- cat .python-version`. The tree has `Dockerfile`, `.dockerignore`, `main.py`, `src/api_demo/app.py`, `src/api_demo/routes/health.py`, and `tests/test_health.py`. The version is `3.14`.
- **fastapi: gates.** Run the four gate commands with `arch-fastapi` and `api-demo`. All must exit `0`, with `7 passed`. See Gotchas for the `ty` result at commit `e6b2e65`.
- **fastapi: run.** Serve the app and call the health route. Run `nv in arch-fastapi-serve api-demo -- "$PWD/.claude/skills/verify-nuv/scripts/serve-healthz.sh" 18765`. Exit code `0`, stdout has `{"status":"ok"}`, and the server log ends with `Granian shutdown completed`.
- **polars: create.** Run `nv nuv arch-polars-create -- new pipe-demo --archetype polars`. Exit code `0`.
- **polars: tree.** Run `nv tree arch-polars-tree pipe-demo` and `nv in arch-polars-pyver pipe-demo -- cat .python-version`. The tree has `src/pipe_demo/_io.py`, `src/pipe_demo/_db.py`, `notebooks/explore.py`, and the empty directories `data/raw` and `data/features`. The version is `3.13`.
- **polars: gates.** Run the four gate commands with `arch-polars` and `pipe-demo`. All exit `0`, with `12 passed`.
- **polars: run.** Run `nv in arch-polars-run pipe-demo -- uv run --frozen python main.py --log-level INFO`. Exit code `0` and stderr has `Starting pipe-demo`.
- **ds: create.** Run `nv nuv arch-ds-create -- new ds-demo --archetype ds`. Exit code `0`.
- **ds: tree.** Run `nv tree arch-ds-tree ds-demo` and `nv in arch-ds-pyver ds-demo -- cat .python-version`. The tree has `src/ds_demo/data.py`, `notebooks/explore.ipynb`, `notebooks/explore_marimo.py`, `data/raw/.gitkeep`, `data/processed/.gitkeep`, and `models/.gitkeep`. The version is `3.13`.
- **ds: gates.** Run the four gate commands with `arch-ds` and `ds-demo`. All exit `0`, with `9 passed`.
- **ds: run.** Run `nv in arch-ds-run ds-demo -- uv run --frozen python main.py --log-level INFO`. Exit code `0` and stderr has `Starting ds-demo`.
- **spark: create.** Run `nv nuv arch-spark-create -- new spark-demo --archetype spark`. Exit code `0`.
- **spark: tree.** Run `nv tree arch-spark-tree spark-demo` and `nv in arch-spark-pyver spark-demo -- cat .python-version`. The tree has `src/spark_demo/session.py`, `src/spark_demo/jobs/example.py`, `notebooks/explore.ipynb`, and `notebooks/explore_marimo.py`. The version is `3.13`.
- **spark: gates.** Run the four gate commands with `arch-spark` and `spark-demo`. All must exit `0`, with `13 passed`. See Gotchas for the `ruff format` result at commit `e6b2e65`.
- **spark: run.** Run `nv in arch-spark-run spark-demo -- uv run --frozen python main.py --help`. Exit code `0` and stdout shows the options `--env`, `--job`, and `--log-level`.
- **Proof.** For each archetype that you drove, report the `-create`, `-tree`, gate, and run evidence files from `.artifacts/verify-nuv/<run-id>/`. Name each archetype that you did not drive.

## Gotchas

- Known failure at commit `e6b2e65` with ty 0.0.104: `uv run --frozen ty check` in a `fastapi` project exits `1`. It reports `warning[deprecated]` for `@asynccontextmanager` at `src/<module>/app.py:13`. Report it as a failure until the template changes.
- Known failure at commit `e6b2e65` with ruff 0.17.5: `uv run --frozen ruff format --check .` in a `spark` project exits `1`. It would reformat `src/<module>/session.py` and `tests/conftest.py`. Report it as a failure until the template changes.
- CI (`.github/workflows/ci.yml`) runs only pytest for `fastapi` and `spark`, so CI does not show these two failures.
- `README.md` in the repo gives default Python `3.13` for `fastapi` and `3.14` for `polars`. The CLI help and the generated `.python-version` give `3.14` for `fastapi` and `3.13` for `polars`. Assert the generated file.
- The first `spark` sync on a cold uv cache downloads PySpark and can take minutes. With a warm cache, `new` took about 20 seconds and the spark tests about 10 seconds.
- The spark tests start a local JVM. Without Java they fail in the session fixture, not in `nuv`.
- `data/raw` and `data/features` in a `polars` project are empty directories. `find -type f` does not show them. `nv tree` does.
- The fastapi `main.py` binds `0.0.0.0:8000` by default. `serve-healthz.sh` binds `127.0.0.1` and the given port. Use a different port for each concurrent run.
- Gate results depend on the newest tool releases at run time. See the first gotcha in [Create a script project](./new-script.md).
