# Workflow: nuv

## Definition of done

All four gates in `40-nuv-stack.md` pass, run in the non-mutating CI form.

Generator changes carry a second, higher bar: **the generated project must be
green too.** Asserting on rendered strings in `tests/test_new.py` proves the
generator emitted text — not that the text is a working project. A change to
`src/nuv/templates/` or `src/nuv/commands/new.py` is not done until a real
scaffold has been created and its own suite has passed.

## Changing an archetype or template

1. Extend `tests/test_new.py` — the 92% branch gate covers the generator, and
   asserting on rendered file *content* is the established convention.
2. Scaffold into a temp directory and run the generated project's suite exactly
   as CI does:
   ```
   uv run --frozen nuv new smoke --at /tmp/smoke --archetype <archetype>
   cd /tmp/smoke && uv sync --frozen && uv run --frozen pytest
   ```
3. If the change touched a `pyproject.toml.tpl`, `dockerfile.tpl`, or
   `readme.md.tpl`, read the rendered output. Brace-escaping mistakes
   (`50-nuv-architecture.md`) surface nowhere else.

## Adding an archetype — all eight, or it is not done

1. `src/nuv/templates/<archetype>/` with its `.tpl` files.
2. `ARCHETYPES` in `src/nuv/cli.py`.
3. `VALID_ARCHETYPES` in `src/nuv/commands/new.py`.
4. A `DEFAULT_PYTHON_VERSIONS` entry.
5. A `_scaffold_<archetype>()` helper **and** an explicit `case` arm in
   `scaffold_files()` — the catch-all arm is FastAPI.
6. Tests in `tests/test_new.py`.
7. A scaffold smoke-test step in `.github/workflows/ci.yml`.
8. A `### <archetype>` section under `## Archetypes` in `README.md`.

All five archetypes are wired through all eight points. Copy `ds` or `polars` as
the reference — their CI steps run the generated project's `ruff check`,
`ruff format --check`, and `ty check` alongside its tests, which is the standard
a new archetype must meet.

## A red archetype you did not touch is usually dependency drift

Templates ship no lockfile — every scaffold resolves its dependencies fresh, so
an upstream release can break an archetype with no change on our side. When CI
fails in an archetype your diff never touched, check the resolved versions in
the generated `uv.lock` before hunting for a regression in your own work.

Prefer fixing the template against stable public API over pinning the dependency
back. Generated projects that ship a deliberately stale framework defeat the
point of the tool. Never assert against private or structural internals of a
framework in a generated test — `fastapi.include_router` stopped flattening
routes into `app.routes` in 0.141, which broke exactly that kind of assertion.

Note also that the smoke steps run in sequence inside one job: the first failing
archetype prevents every later archetype and the wheel checks from running at
all. A green run above the failure line is not evidence they pass.

## Generator tests stay dependency-free

`tests/test_new.py` stubs heavy runtime dependencies (`_install_pyspark_stubs`)
so nuv's own suite needs neither pyspark nor a JVM. Never add an archetype's
runtime stack to nuv's `[dependency-groups] dev` or import it unguarded in a
test. Follow the file's existing shape: flat `test_*` functions, `_`-prefixed
module-level helpers, `tmp_path` / `caplog` / `monkeypatch` fixtures, and
`@pytest.mark.parametrize` for input tables.

## Branches and PRs

- Work on a branch and merge through a PR — history is `summary (#NN)`. Do not
  commit directly to `main`.
- CI must be green to merge: lint and type check on 3.14; tests on 3.11 and
  3.14; scaffold smoke tests for all five archetypes; and wheel install checks.

## Packaging changes need their own proof

The CI wheel smoke test only runs `nuv --help`, which passes even if no `.tpl`
file shipped. If a change touches the hatch `include`/`packages` config or moves
template files, prove it by scaffolding **from the built wheel**, not the source
tree:

```
uv build && uvx --from dist/*.whl nuv new wheelcheck --at /tmp/wheelcheck --archetype <archetype>
```

## Hygiene

- Never hand-edit `uv.lock`; regenerate it with uv.
- Keep `README.md`'s archetype list in sync with what `nuv new` accepts.
