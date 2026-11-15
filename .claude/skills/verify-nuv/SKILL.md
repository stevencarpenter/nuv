---
name: verify-nuv
description: Drive the nuv CLI (`nuv new`, the project scaffolder in this repo) from this checkout the way a user does, and capture proof. Use after a change to `src/nuv/` (CLI options, validation, cleanup, templates, archetypes) or to packaging, when you must prove that `nuv new` still creates a working project. Unit tests mock `uv`; this skill runs the real `uv sync` and the generated project's own gates.
---

# Verify nuv

`nuv` is a short-lived CLI. Its one command, `nuv new <name>`, writes a project directory, runs
`uv sync` in it, and logs or runs a `uv tool install`. No server exists. A drive is one command in
a scratch directory, and the proof is the recorded command, output, exit code, the generated tree,
and the result of the generated project's gates.

The unit tests in `tests/test_new.py` patch `subprocess.run`. They do not prove that a generated
project syncs, passes its tests, or runs. This skill does.

Read [`features/README.md`](features/README.md) before you drive. It lists every user-facing
feature and has one recipe file per feature.

## Launch

Run every command from the repo root. The helper is
`.claude/skills/verify-nuv/scripts/nuv-verify.sh <run-id> <subcommand>`.

Shell variables do not persist between tool calls. Start each shell call with this line, and
use the same run id for the whole run:

```bash
RUN=20261115-a; nv() { .claude/skills/verify-nuv/scripts/nuv-verify.sh "$RUN" "$@"; }
```

Then start the run:

```bash
nv init
```

`init` runs `uv sync --frozen` in the repo, makes a scratch directory outside the repo
(`$TMPDIR/nuv-verify-<run-id>.XXXXXX`), and makes the evidence directory
`.artifacts/verify-nuv/<run-id>/`. It prints both paths. Set `NUV_VERIFY_SCRATCH_ROOT` before
`init` to put the scratch directory under a different parent.

The run is ready when `nv doctor` prints `DOCTOR OK`. There is no process to keep alive and no
seed data. Each feature recipe starts from an empty scratch directory or names the project it
needs.

Requirements: `uv` (checked with 0.13.8), network access to PyPI or a warm uv cache, and Java
for the `spark` archetype tests (checked with OpenJDK 25; CI uses 17).

## Doctor

```bash
nv doctor
```

Doctor is read-only apart from its own evidence file `doctor.txt`. Run it first and whenever a
result looks wrong. It prints the commit, the count of uncommitted files, the `uv` version, the
file that `import nuv` loads, the `nuv` version, the scratch path, and the `uv tool dir`.

It fails when:

- `nuv` does not load from `<repo>/src/nuv/__init__.py`. You would be driving a different build.
- `uv tool dir` is not inside the scratch directory. `--install editable` would then write to the
  user's real tool directory.

Never run a bare `nuv`. On a developer machine `nuv` on `PATH` can be the released tool from
`uv tool install nuv`, not this checkout.

## Drive

Four subcommands drive and record. Each takes a label, which names the evidence files.

| Command | Action |
| --- | --- |
| `nv nuv <label> [--expect N] [<dir>] -- <nuv args>` | Runs `uv run --project <repo> --frozen nuv <nuv args>` with the scratch directory (or `<dir>` in it) as the current directory. |
| `nv in <label> [--expect N] [<dir>] -- <command>` | Runs any command in the scratch directory, or in `<dir>` in it. Use it for the generated project's gates. |
| `nv tree <label> [<dir>]` | Lists every file and directory under the scratch directory or `<dir>`, dotfiles included, without `.venv`. |
| `nv cleanup` | Removes the scratch directory. |

`--expect N` is the expected exit code (default `0`). The helper exits non-zero when the actual
exit code differs. Use `--expect 1` or `--expect 2` to prove a refusal.

Example, the default journey:

```bash
nv nuv script-create -- new demo-tool
nv tree script-tree demo-tool
nv in script-pytest demo-tool -- uv run --frozen pytest
```

Stable handles for assertions:

- Exit codes. `0` success. `1` a refusal or failure from `nuv` (stderr line starts with
  `ERROR nuv.commands.new:`), and also bare `nuv` with no command. `2` a usage error from click
  (stderr has `Error: Invalid value for`).
- Log lines on stderr, format `LEVEL logger: message`. At the default `WARNING` level a
  successful `new` prints only the two lines `Run this to install the generated tool:` and
  `uv tool install --editable <path>`. `created <path>/` appears only with `--log-level INFO`.
- The generated tree from `nv tree`, and the content of `.python-version`.
- The generated project's gates: `uv run --frozen pytest`, `uv run --frozen ruff check .`,
  `uv run --frozen ruff format --check .`, `uv run --frozen ty check`.

Isolation: each run id has its own scratch directory, evidence directory, and uv tool
directories, so two runs can proceed at the same time. They share the repo working tree.
`uv run --project` reads `src/` live, so an edit to `src/nuv/` during a run changes the app under
test. Run `nv doctor` again after any edit and record the new state.

## Evidence

Every `nv nuv` and `nv in` call writes four files to `.artifacts/verify-nuv/<run-id>/`:
`<label>.cmd` (directory and exact command), `<label>.out`, `<label>.err`, and `<label>.exit`.
`nv tree` writes `<label>.tree`. `nv doctor` writes `doctor.txt`. `.artifacts/` is gitignored.

Proof standards:

- Use the real user path: the `nuv` command line. Do not import `run_new()` or call
  `scaffold_files()` as proof, and do not cite the unit tests as proof of generated-project
  behavior, because they mock `uv`.
- Record the action and the resulting state. For a `new`, that is the command evidence, the tree,
  and at least one gate of the generated project.
- Check side effects. A refusal must leave no directory and must leave existing content
  unchanged. A failed run must leave no target unless `--keep-on-failure` was given.
- `--install command-only` is the default and is a dry run of the install step. It was checked
  by observation: it logs the command, and `uv tool list` shows no new tool. `uv sync` still
  runs and still uses the network. Prove a dry-run claim with `nv in <label> -- uv tool list`,
  not with the option name.
- To prove release packaging (the `.tpl` files inside the wheel), drive the wheel as in
  `features/cli-and-wheel.md`. `nuv --help` from a wheel reads no template and proves nothing
  about templates.
- A proof that drives one archetype is incomplete when the change touches shared code
  (`scaffold_files`, `render_template`, `run_new`, templates in `shared/`). Drive each archetype
  that the change can reach.

## Cleanup

```bash
nv cleanup
```

Cleanup removes only the scratch directory that `init` made for this run id, with the generated
projects and the scratch uv tool directories in it. It keeps `.artifacts/verify-nuv/<run-id>/`
and prints the count of evidence files. Run it after a failed attempt too.

The helper starts no background process. `serve-healthz.sh` starts one server and stops that
same process by its PID before it exits. Never stop a process by name.

The uv cache keeps downloaded packages and the wheel environment from `uvx`. Leave the cache.

## Helpers

Both scripts are executable.

- `.claude/skills/verify-nuv/scripts/nuv-verify.sh <run-id> <init|doctor|nuv|in|tree|cleanup> ...`
  is the harness described above.
- `.claude/skills/verify-nuv/scripts/serve-healthz.sh <port>` starts a generated `fastapi`
  project on `127.0.0.1:<port>`, prints the body of `GET /healthz`, stops the server, and prints
  the server log. Run it through the harness with the generated project as the directory:

  ```bash
  nv in fastapi-serve api-demo -- "$PWD/.claude/skills/verify-nuv/scripts/serve-healthz.sh" 18765
  ```

## Surfaces this skill does not drive

- The Claude Code plugin skill in `plugins/nuv/skills/util/SKILL.md`.
- The PyPI publish workflow in `.github/workflows/publish-pypi.yml`.
- Docker builds of the generated `fastapi` project.
- The optional `notebooks` dependency group of the `spark`, `polars`, and `ds` projects.
