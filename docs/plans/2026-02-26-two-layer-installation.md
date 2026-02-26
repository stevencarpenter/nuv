# Two-layer installation strategy for `nuv` (2026)

## Goal

Enable two "installation" layers:

1. **Generator install layer**: users can run `nuv` from anywhere to bootstrap a project.
2. **Generated-project install layer**: a project created by `nuv` is immediately installable/runnable with minimal extra ceremony.

This document explores practical options aligned with modern `uv` + Python conventions and recommends a phased rollout.

## Current baseline

`nuv` already supports global install/use patterns:

- `uv tool install git+https://.../nuv`
- `uvx --from git+https://.../nuv nuv new my-tool`

Generated projects are synced with `uv sync`, so they are ready for local development via `uv run ...`.

## Layer 1: install and run `nuv` anywhere

### Option A — keep tool install as the primary path (recommended)

**Flow**

- User runs `uv tool install ...nuv`
- `nuv` is available on PATH globally

**Why this matches 2026 norms**

- `uv tool install` is the expected analogue of `pipx`-style isolated CLI installs.
- Reproducible and Python-version-aware without manual virtualenv management.
- Minimal maintenance burden in `nuv` itself.

**Improvements to add**

- Add short "quick install" copy for macOS/Linux/Windows.
- Add a shell completion one-liner (`nuv --install-completion`) eventually.
- Publish tagged releases and prefer `uv tool install nuv==X.Y.Z` once on index.

### Option B — zero-install launcher via `uvx` (recommended as secondary)

**Flow**

- User runs `uvx --from <source> nuv ...`

**Best use**

- Trial usage, CI flows, and one-off scaffolding.

**Tradeoffs**

- Slight startup overhead vs a preinstalled tool.
- Still excellent for "run anywhere" docs and demos.

### Option C — curl/powershell bootstrap scripts (possible, lower priority)

**Flow**

- User runs installer script that checks for `uv` and installs/configures `nuv`.

**Pros**

- Fast onboarding UX for non-expert users.

**Cons**

- Security/review burden.
- More OS-specific logic and maintenance.

## Layer 2: install the generated project immediately

There are two fundamentally different interpretations of "installed":

1. **Dev-installed**: project is ready via `uv run ...` and editable development.
2. **Tool-installed**: project exposes an executable command globally (or user-local PATH) via `uv tool install`.

A good strategy is to support both, with explicit defaults.

### Option 2A — development install by default (recommended future default)

After scaffold:

- Run `uv sync` (already done).
- Project is immediately runnable in managed env:
  - `uv run <entrypoint>`
  - `uv run pytest`, etc.

**Enhancements**

- Print a post-create success panel with next commands.
- Add `--no-sync` for fast offline scaffolding.
- Add `--frozen` for reproducible lockfile-first setup in CI.

### Option 2B — editable tool install for generated project (implemented default today)

Add a `--install` mode to `nuv new`:

- `nuv new my-tool --install editable`

Suggested implementation contract:

1. Scaffold package-ready layout (`src/<module_name>/...`) and `project.scripts` entrypoint.
2. Run `uv sync`.
3. Run `uv tool install --editable <target>` (or emit exact command if policy is "no global side effects by default").

**Why this can still work as a default in the current implementation**

- Global tool installs modify user environment, so the command remains explicit and configurable via `--install`.
- `nuv` still offers conservative alternatives (`--install none` and `--install command-only`) for CI and dry-run style workflows.

### Option 2C — always global-install generated tool (not recommended default)

**Pros**

- Maximum immediate convenience.

**Cons**

- Surprising side effects.
- Name collisions on PATH.
- Harder behavior in CI and ephemeral environments.

## Template architecture changes needed for Layer 2B

To make generated projects install cleanly as tools, evolve templates from a single `main.py` script to a package-first layout:

- `src/{module_name}/__init__.py`
- `src/{module_name}/cli.py` containing `main()`
- optional `src/{module_name}/__main__.py`
- `pyproject.toml` with:
  - explicit build backend (`hatchling` or equivalent)
  - `[project.scripts] {name} = "{module_name}.cli:main"`

Testing updates:

- Import CLI from package path in tests.
- Add smoke test for installed console script invocation pattern.

## Recommended phased roadmap

### Phase 1 (immediate)

- Keep current install paths (`uv tool install`, `uvx`) and improve docs.
- Add explicit "dev-installed by default via `uv sync`" messaging.
- Print post-scaffold next-step commands.

### Phase 2

- Add `--install` flag with values:
  - `editable` (default today; runs `uv tool install --editable <target>`)
  - `none` (skip tool install)
  - `command-only` (print command without executing)

### Phase 3

- Add a package archetype tuned for global CLI tools.
- Keep script archetype lightweight for quick scripts.

## Example UX

### Install `nuv` once

```bash
uv tool install git+https://github.com/stevencarpenter/nuv
```

### Bootstrap + local dev-ready project

```bash
mkdir my-tool && cd my-tool
nuv new my-tool --at .
uv run my-tool --help  # once scripts/archetype supports it
```

### Bootstrap + editable global install

```bash
nuv new my-tool --install editable
my-tool --help
```

## Decision summary

- **Default**: scaffold + `uv sync` + editable tool install for immediate command availability.
- **Alternatives**: conservative modes remain available via `--install none` and `--install command-only`.
- **Architecture**: introduce package-first template path to make install behavior robust.

This balances ease-of-use, explicitness, and predictable side effects while staying idiomatic with `uv` conventions.
