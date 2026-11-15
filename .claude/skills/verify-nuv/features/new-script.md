# Create a script project

`nuv new <name>` with no other option creates `./<name>/` as a single-file click CLI project,
syncs its dependencies, and prints the command that installs it as a tool. The new project has
passing tests, clean lint, and clean type checks without any edit.

## Sub-features

- `script-create` creates the project and exits `0`.
- `script-tree` writes the documented files and Python version.
- `script-gates` gives a project whose pytest, ruff, and ty gates pass.
- `script-run` gives a `main.py` that runs.

## How to get to it (user POV)

- Run `nuv new <name>` in the directory that will hold the project.
- Run `uvx nuv new <name>` without an install. See [Root command and wheel](./cli-and-wheel.md).

## Driving it with nuv-verify

Preconditions:

- The baseline in [README](./README.md) holds.
- The scratch directory has no `demo-tool` entry.

- **Create.** Run `nv nuv script-create -- new demo-tool`. Exit code `0`. Stderr ends with `WARNING nuv.commands.new: Run this to install the generated tool:` and `WARNING nuv.commands.new: uv tool install --editable <scratch>/demo-tool`.
- **Tree.** List the project. Run `nv tree script-tree demo-tool`. The files are exactly `.gitignore`, `.python-version`, `_logging.py`, `main.py`, `pyproject.toml`, `README.md`, `tests/__init__.py`, `tests/test_main.py`, and `uv.lock`.
- **Python version.** Read the pinned version. Run `nv in script-pyver demo-tool -- cat .python-version`. Stdout is `3.14`.
- **Tests.** Run the generated tests. Run `nv in script-pytest demo-tool -- uv run --frozen pytest`. Exit code `0`, `2 passed`, and `Required test coverage of 100% reached`.
- **Lint.** Run `nv in script-ruff demo-tool -- uv run --frozen ruff check .` and `nv in script-format demo-tool -- uv run --frozen ruff format --check .`. Both exit `0`.
- **Types.** Run `nv in script-ty demo-tool -- uv run --frozen ty check`. Exit code `0` and `All checks passed!`.
- **Run.** Start the generated CLI. Run `nv in script-run demo-tool -- uv run --frozen python main.py --help`. Exit code `0` and stdout shows `Usage: main.py [OPTIONS]` with a `--log-level` option.
- **Proof.** Report `script-create.*`, `script-tree.tree`, and the gate evidence files from `.artifacts/verify-nuv/<run-id>/`.

## Gotchas

- The generated `pyproject.toml` gives lower bounds, not pins. `uv sync` resolves the newest pytest, ruff, and ty at run time. A new gate failure can come from a tool release. To attribute it, run the same recipe on the base commit in a second checkout.
- A successful `new` prints no `created` line at the default log level. Use the exit code and the tree, or add `--log-level INFO`.
- `uv.lock` and `.venv` come from `uv sync`, not from a template. Their absence means the sync did not run.
- The name `demo-tool` becomes the module name `demo_tool`. A name that is a Python keyword or starts with a digit is refused. See [Refusals and failures](./new-failures.md).
