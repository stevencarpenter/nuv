# nuv verification map

This directory is the maintained source for verifying the user-facing behavior of `nuv`. Read
this index before you drive the CLI, then use the matching feature file as the recipe.

## Baseline preconditions

- The current directory is the repo root.
- `uv` is on `PATH`, and PyPI or a warm uv cache is reachable.
- `nv init` succeeded for a new run id, and `nv doctor` prints `DOCTOR OK`.
- The scratch directory is empty apart from what earlier steps of the same recipe made.
- Never drive a bare `nuv` from `PATH`. Never reuse the scratch directory of a different run.

## Driving conventions

- `nv` means `.claude/skills/verify-nuv/scripts/nuv-verify.sh "$RUN"`. Start each shell call with
  `RUN=<run-id>; nv() { .claude/skills/verify-nuv/scripts/nuv-verify.sh "$RUN" "$@"; }`.
- Run CLI actions with `nv nuv <label> [--expect N] -- <nuv args>`.
- Run actions in a generated project with `nv in <label> <project-dir> -- <command>`.
- Treat every command as literal. Keep names, labels, and flags unchanged.
- Each recipe uses its own project names, so recipes can share one run.
- A step passes only when the exit code matches and the stated output is present.

## Proof and skip reporting

- CLI proof is the `.cmd`, `.out`, `.err`, and `.exit` files of the step in
  `.artifacts/verify-nuv/<run-id>/`.
- Creation proof also includes the `.tree` file and at least one gate of the generated project.
- Refusal and failure proof also includes a tree that shows no leftover directory, and unchanged
  content for a path that existed before.
- Record the feature file and the sub-feature ID with every result you report.
- Report a step that cannot run with the attempted command and the unmet precondition.
- Do not report a skipped archetype or entry point as verified through a different one.
- A step that fails with a reason listed under `Gotchas` is still a failure. Report it with that
  reason. Do not remove the step.

## Feature entry contract

Each feature file starts with an H1 title and one paragraph that describes the user-visible
behavior. It then uses exactly four H2 sections in this order.

1. `Sub-features` lists short IDs with one line for each behavior.
2. `How to get to it (user POV)` lists every user entry point.
3. `Driving it with nuv-verify` starts with `Preconditions:` and uses labeled bullets that pair
   each user action with an exact command and observable result.
4. `Gotchas` lists traps that can waste or invalidate a verification run.

Keep implementation details out of the map. Name only user paths, stable handles, required
state, commands, and observable proof.

## Features

- [Create a script project](./new-script.md) covers the default `nuv new <name>` journey: tree,
  Python version, green gates, and a runnable `main.py`.
- [Create a project from each archetype](./new-archetypes.md) covers `--archetype` for `util`,
  `fastapi`, `polars`, `ds`, and `spark`.
- [Options of `nuv new`](./new-options.md) covers `--at`, `--python-version`, `--install`, and
  `--log-level`.
- [Refusals and failures](./new-failures.md) covers invalid names, an existing target, usage
  errors, a failed `uv sync`, and `--keep-on-failure`.
- [Root command and wheel](./cli-and-wheel.md) covers `nuv` with no command, help, and `nuv new`
  from a built wheel through `uvx`.
