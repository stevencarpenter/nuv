# Stack: nuv

## What this project is

`nuv` is a CLI that scaffolds opinionated uv-based Python projects. Almost all
the code here is a *generator*: files under `src/nuv/templates/**/*.tpl` are
rendered into other people's repositories. Two things must be green for a
change to count — nuv itself, and the projects nuv emits. Passing the first
while breaking the second is the characteristic failure mode of this codebase.

## Toolchain (overrides the bundled "Python 3.14+" rule)

- `requires-python = ">=3.11"` and CI runs the test matrix on 3.11 **and** 3.14.
  Do not use syntax or stdlib APIs newer than 3.11 in `src/nuv/`. The local
  interpreter pin (`.python-version` = 3.14) is not the support floor.
- `uv` only — never pip, poetry, or pipx.
- Generated projects target a *different*, per-archetype Python version
  (`DEFAULT_PYTHON_VERSIONS`); do not conflate the two. Template content is not
  bound by nuv's own 3.11 floor.

## Gates — all four must pass, in the non-mutating CI form

```
uv run --frozen ruff check src/ tests/
uv run --frozen ruff format --check src/ tests/
uv run --frozen ty check src/
uv run --frozen pytest
```

Build is `uv build`. The justfile offers `just check` and `just all`, but
`just lint` **rewrites files** (`ruff check --fix` + `ruff format`) instead of
failing — never treat a passing `just lint` as evidence a gate is green.

## Lock-ins — do not change without an explicit reason

- ruff: `line-length = 180`, `target-version = "py311"`, lint select
  `E, F, I, UP, B, SIM`. The wide line length is deliberate; do not reflow code
  to a narrower width.
- Coverage: branch coverage with `--cov-fail-under=92`.
  (`.github/copilot-instructions.md` claims 100% — that is stale. 92 is the
  enforced number.)
- Type checker is `ty`. Not mypy, not pyright. It runs against `src/` only.
- nuv's runtime dependency set is exactly `click`. Adding one means updating
  `pyproject.toml` **and** `uv.lock`. Dependencies belonging to an archetype
  live in that archetype's `pyproject.toml.tpl`, never in nuv's.

## Repo-specific conventions

- No `print()` for user-facing output. Each module uses
  `log = logging.getLogger(__name__)`; `_logging.configure()` is called exactly
  once, from the click group in `cli.py`. Generated projects ship the same
  `_logging.py` pattern, so it must survive into templates unchanged.
- Public functions carry full annotations and PEP 604 unions (`X | None`).
