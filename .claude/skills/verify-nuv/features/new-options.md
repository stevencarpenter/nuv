# Options of `nuv new`

`nuv new` takes options that change where the project goes, which Python version it pins, what
happens at the install step, and how much `nuv` logs. `--keep-on-failure` is in
[Refusals and failures](./new-failures.md), and `--archetype` is in
[Create a project from each archetype](./new-archetypes.md).

## Sub-features

- `opt-at` creates the project at an explicit path and creates missing parent directories.
- `opt-python-version` pins a Python version other than the archetype default.
- `opt-install-command-only` logs the install command and installs nothing (default).
- `opt-install-none` skips the install step and logs no install command.
- `opt-install-editable` installs the generated project as an editable uv tool.
- `opt-log-level` makes `nuv` log the `created` line at `INFO`.

## How to get to it (user POV)

- Run `nuv new <name> --at <path>`.
- Run `nuv new <name> --python-version <MAJOR.MINOR>`.
- Run `nuv new <name> --install command-only`, `--install none`, or `--install editable`.
- Run `nuv --log-level <LEVEL> new <name>`. The option goes before `new`.

## Driving it with nuv-verify

Preconditions:

- The baseline in [README](./README.md) holds.
- The scratch directory has no `deep`, `py-tool`, `co-tool`, `none-tool`, or `ed-tool` entry.
- `nv doctor` shows a `uv tool dir` inside the scratch directory.

- **Explicit path.** Run `nv nuv opt-at -- new at-tool --at deep/nested/at-tool --install none`. Exit code `0`. Then run `nv tree opt-at-tree deep` and `nv in opt-at-top --expect 1 -- test -e at-tool`. The tree has `./nested/at-tool/pyproject.toml` and `./nested/at-tool/uv.lock`. Exit code `1` of the second command shows that the scratch directory has no `at-tool` entry at its top level.
- **Python version.** Run `nv nuv opt-pyver -- new py-tool --python-version 3.13 --install none`. Exit code `0`. Then run `nv in opt-pyver-file py-tool -- cat .python-version`. Stdout is `3.13`. Then run `nv in opt-pyver-pytest py-tool -- uv run --frozen pytest`. Exit code `0`.
- **Install command-only.** Run `nv nuv opt-cmdonly -- new co-tool`. Exit code `0` and stderr has `uv tool install --editable <scratch>/co-tool`. Then run `nv in opt-cmdonly-list -- uv tool list`. Stdout does not list `co-tool`. When no tool is installed, stdout is empty and stderr is `No tools installed`.
- **Install none.** Run `nv nuv opt-none -- --log-level INFO new none-tool --install none`. Exit code `0`. Stderr has `INFO nuv.commands.new: created <scratch>/none-tool/` and does not have `uv tool install`.
- **Install editable.** Run `nv nuv opt-editable -- new ed-tool --install editable`. Exit code `0` and stderr has `Installed 1 executable: ed-tool`. Then run `nv in opt-editable-list -- uv tool list`. Stdout lists `ed-tool v0.1.0`. Then run `nv in opt-editable-run -- .uv-bin/ed-tool --help`. Exit code `0` and stdout shows `Usage: ed-tool [OPTIONS]`.
- **Log level.** The `opt-none` step is the proof for `INFO`. Compare it with `opt-cmdonly.err`, which has no `created` line.
- **Proof.** Report the evidence files of each step from `.artifacts/verify-nuv/<run-id>/`, and `opt-cmdonly-list.out` and `opt-editable-list.out` as the side-effect proof for the install modes.

## Gotchas

- `--install editable` runs `uv tool install --editable`. Outside the harness that command writes to the user's real tool directory (`uv tool dir`) and adds an executable to their bin directory. Drive it only through `nv`, which sets `UV_TOOL_DIR` and `UV_TOOL_BIN_DIR` to scratch paths. Check `nv doctor` first.
- `uv tool install` prints a warning that `.uv-bin` is not on `PATH`. That warning is expected in the harness.
- `uv tool list` shows every tool of the run. Run the `opt-cmdonly-list` step before the `opt-editable` step, or check for the tool name, not for empty output.
- A relative `--at` path is relative to the current directory of the command, which is the scratch directory in the harness.
- `--at` to a missing parent creates the parents. If the run then fails, `nuv` removes only the last directory and leaves the new parents.
- `--log-level` is an option of `nuv`, not of `new`. `nuv new x --log-level INFO` is a usage error with exit code `2`.
- `--python-version` accepts only `MAJOR.MINOR`. A version that uv cannot find fails at `uv sync`, not at validation. See [Refusals and failures](./new-failures.md).
