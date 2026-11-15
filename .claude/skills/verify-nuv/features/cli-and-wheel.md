# Root command and wheel

`nuv` with no command prints the help and exits `1`. `nuv --help`, `nuv -h`, and
`nuv new --help` print help and exit `0`. Users install `nuv` from a wheel (`uv tool install nuv`)
or run it with `uvx nuv new <name>`, so the built wheel must contain the templates and must
create a working project.

## Sub-features

- `root-bare` prints the group help and exits `1` when no command is given.
- `root-help` prints the group help and exits `0` for `--help` and `-h`.
- `new-help` prints every option of `new` with its choices and defaults.
- `wheel-build` builds a wheel from the checkout.
- `wheel-new` creates a working project with `nuv` from that wheel through `uvx`.

## How to get to it (user POV)

- Run `nuv`.
- Run `nuv --help` or `nuv -h`.
- Run `nuv new --help` or `nuv new -h`.
- Run `uvx nuv new <name>`, or `uv tool install nuv` and then `nuv new <name>`.

## Driving it with nuv-verify

Preconditions:

- The baseline in [README](./README.md) holds.
- The scratch directory has no `dist` or `wheel-tool` entry.

- **Bare command.** Run `nv nuv root-bare --expect 1 --`. Stdout starts with `Usage: nuv [OPTIONS] [COMMAND] [ARGS]...` and lists the command `new`.
- **Group help.** Run `nv nuv root-help -- --help` and `nv nuv root-help-short -- -h`. Both exit `0` with the same stdout as the bare command.
- **Command help.** Run `nv nuv new-help -- new --help`. Exit code `0`. Stdout lists `--at`, `--archetype [script|spark|fastapi|polars|ds|util]`, `--python-version`, `--install [editable|none|command-only]`, and `--keep-on-failure`, with the defaults `script` and `command-only`.
- **Build wheel.** Build into the scratch directory. Run `nv in wheel-build -- uv build --project "$PWD" --wheel --out-dir dist`. Exit code `0` and stderr has `Successfully built dist/nuv-`.
- **Wheel origin.** Show that `uvx` loads `nuv` from the wheel, not from the checkout. Run `nv in wheel-where -- sh -c 'uvx --from dist/nuv-*.whl python -c "import nuv; print(nuv.__file__)"'`. Stdout is a path in the uv cache that ends with `site-packages/nuv/__init__.py`. It is not under the repo.
- **Create from wheel.** Run `nv in wheel-new -- sh -c 'uvx --from dist/nuv-*.whl nuv new wheel-tool --archetype util --install none'`. Exit code `0`.
- **Tree and gate.** Run `nv tree wheel-tree wheel-tool` and `nv in wheel-pytest wheel-tool -- uv run --frozen pytest`. The tree has `AGENTS.md`, `src/wheel_tool/main.py`, and `uv.lock`. Pytest exits `0` with `3 passed`.
- **Other archetypes from the wheel.** After any packaging change, or a change that adds or moves a template file, repeat the create step from the wheel for `script`, `spark`, `fastapi`, `polars`, and `ds`, with a new project name for each. The `util` check alone does not show that the other archetypes' templates are in the wheel.
- **Proof.** Report `root-bare.*`, `new-help.out`, `wheel-build.err`, `wheel-where.out`, `wheel-new.*`, `wheel-tree.tree`, and `wheel-pytest.*` from `.artifacts/verify-nuv/<run-id>/`.

## Gotchas

- `nuv --help` from a wheel reads no template file. It does not prove that the `.tpl` files are in the wheel. Only a `new` from the wheel does.
- `uv build` without `--out-dir` writes to `dist/` in the repo. The repo `dist/` can hold wheels of older versions. Always build into the scratch directory and use that wheel.
- `nuv` on `PATH` and `nv nuv` do not use the wheel. Only the `uvx --from dist/nuv-*.whl` steps do.
- The wheel glob needs a shell, so the wheel steps use `sh -c`. With more than one wheel in `dist`, the glob breaks the command.
- `uvx` chooses its own Python for the `nuv` environment (3.15 in the checked run). `requires-python` in `pyproject.toml` is `>=3.11`.
- `uvx` keeps the wheel environment in the uv cache. The scratch path is new for each run, so a new run does not reuse an old wheel.
- The bare command exits `1`, not `0`. A script that treats `nuv` with no arguments as success is wrong.
