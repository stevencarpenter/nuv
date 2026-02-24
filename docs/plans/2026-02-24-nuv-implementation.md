# nuv Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build `nuv`, an installable uv tool that scaffolds opinionated Python uv projects with passing tests and quality tooling out of the box.

**Architecture:** A `src/` layout Python package with a `nuv new` subcommand. Templates live as `.tpl` files inside the package, rendered via `stdlib string.Template`. File generation is pure Python; `uv sync` is the only subprocess call.

**Tech Stack:** Python 3.14+, uv, argparse, string.Template, pytest + pytest-cov (100%), ruff, ty

---

## Reference: Design Doc

Full design at `docs/plans/2026-02-24-nuv-design.md`. Read it before starting.

---

### Task 1: Bootstrap the project

**Files:**
- Create: `pyproject.toml`
- Create: `src/nuv/__init__.py`
- Create: `src/nuv/cli.py`
- Create: `src/nuv/commands/__init__.py`
- Create: `src/nuv/commands/new.py`
- Create: `tests/__init__.py`
- Create: `tests/test_new.py`

**Step 1: Write `pyproject.toml`**

```toml
[project]
name = "nuv"
version = "0.1.0"
description = "Scaffold opinionated uv Python projects"
readme = "README.md"
requires-python = ">=3.14"
dependencies = []

[project.scripts]
nuv = "nuv.cli:main"

[dependency-groups]
dev = [
    "pytest>=8",
    "pytest-cov>=6",
    "ruff>=0.9",
    "ty>=0.0.1a1",
]

[tool.pytest.ini_options]
addopts = "--cov=nuv --cov-report=term-missing --cov-fail-under=100"

[tool.ruff]
target-version = "py314"

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B", "SIM"]

[tool.coverage.run]
branch = true

[tool.coverage.report]
exclude_lines = ["if __name__ == .__main__.:"]
```

**Step 2: Write empty init files**

`src/nuv/__init__.py` — empty file.
`src/nuv/commands/__init__.py` — empty file.
`tests/__init__.py` — empty file.

**Step 3: Write `src/nuv/cli.py` stub**

```python
import argparse
import sys
from typing import Sequence


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="nuv",
        description="Scaffold opinionated uv Python projects.",
    )
    subparsers = parser.add_subparsers(dest="command", metavar="<command>")

    new_parser = subparsers.add_parser("new", help="Create a new project.")
    new_parser.add_argument("name", help="Project name.")
    new_parser.add_argument("--at", metavar="PATH", help="Target directory (default: ./<name>).")

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    from nuv.commands.new import run_new

    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "new":
        return run_new(args.name, at=args.at)

    parser.print_help()
    return 1
```

**Step 4: Write `src/nuv/commands/new.py` stub**

```python
from pathlib import Path


def run_new(name: str, *, at: str | None = None) -> int:
    return 0
```

**Step 5: Write a placeholder test so pytest can run**

In `tests/test_new.py`:

```python
from nuv.cli import main


def test_no_command_returns_1() -> None:
    assert main([]) == 1
```

**Step 6: Sync and verify the project runs**

```bash
cd ~/personal/nuv
uv sync
uv run pytest
```

Expected: 1 test passes (coverage will be low — that's fine for now).

**Step 7: Commit**

```bash
git init
git add pyproject.toml src/ tests/
git commit -m "feat: bootstrap nuv project skeleton"
```

---

### Task 2: Name validation

**Files:**
- Modify: `src/nuv/commands/new.py`
- Modify: `tests/test_new.py`

Valid names: alphanumeric, hyphens, underscores. No spaces, no leading hyphens, not empty.

**Step 1: Write failing tests**

Add to `tests/test_new.py`:

```python
import pytest
from nuv.commands.new import validate_name


def test_validate_name_simple() -> None:
    assert validate_name("my-project") == "my-project"


def test_validate_name_underscores() -> None:
    assert validate_name("my_project") == "my_project"


def test_validate_name_empty() -> None:
    with pytest.raises(ValueError, match="empty"):
        validate_name("")


def test_validate_name_spaces() -> None:
    with pytest.raises(ValueError, match="spaces"):
        validate_name("my project")


def test_validate_name_leading_hyphen() -> None:
    with pytest.raises(ValueError, match="leading hyphen"):
        validate_name("-bad")


def test_validate_name_invalid_chars() -> None:
    with pytest.raises(ValueError, match="invalid"):
        validate_name("bad/name")
```

**Step 2: Run to verify they fail**

```bash
uv run pytest tests/test_new.py -k "validate" -v
```

Expected: ImportError or AttributeError — `validate_name` not defined yet.

**Step 3: Implement `validate_name`**

Add to `src/nuv/commands/new.py`:

```python
import re


def validate_name(name: str) -> str:
    if not name:
        raise ValueError("Name cannot be empty.")
    if " " in name:
        raise ValueError("Name cannot contain spaces.")
    if name.startswith("-"):
        raise ValueError("Name cannot start with a leading hyphen.")
    if not re.fullmatch(r"[a-zA-Z0-9_\-]+", name):
        raise ValueError(f"Name contains invalid characters: {name!r}")
    return name
```

**Step 4: Run tests to verify they pass**

```bash
uv run pytest tests/test_new.py -k "validate" -v
```

Expected: 6 tests pass.

**Step 5: Commit**

```bash
git add src/nuv/commands/new.py tests/test_new.py
git commit -m "feat: add name validation for nuv new"
```

---

### Task 3: Target directory resolution

**Files:**
- Modify: `src/nuv/commands/new.py`
- Modify: `tests/test_new.py`

**Step 1: Write failing tests**

```python
from pathlib import Path
from nuv.commands.new import resolve_target


def test_resolve_target_default(tmp_path: Path) -> None:
    target = resolve_target("my-project", at=None, cwd=tmp_path)
    assert target == tmp_path / "my-project"


def test_resolve_target_explicit(tmp_path: Path) -> None:
    explicit = tmp_path / "elsewhere"
    target = resolve_target("my-project", at=str(explicit), cwd=tmp_path)
    assert target == explicit


def test_resolve_target_already_exists(tmp_path: Path) -> None:
    existing = tmp_path / "my-project"
    existing.mkdir()
    with pytest.raises(ValueError, match="already exists"):
        resolve_target("my-project", at=None, cwd=tmp_path)
```

**Step 2: Run to verify they fail**

```bash
uv run pytest tests/test_new.py -k "resolve_target" -v
```

Expected: ImportError.

**Step 3: Implement `resolve_target`**

Add to `src/nuv/commands/new.py`:

```python
def resolve_target(name: str, *, at: str | None, cwd: Path) -> Path:
    target = Path(at) if at else cwd / name
    if target.exists():
        raise ValueError(f"Directory already exists: {target}")
    return target
```

**Step 4: Run tests to verify they pass**

```bash
uv run pytest tests/test_new.py -k "resolve_target" -v
```

Expected: 3 tests pass.

**Step 5: Commit**

```bash
git add src/nuv/commands/new.py tests/test_new.py
git commit -m "feat: add target directory resolution for nuv new"
```

---

### Task 4: Template rendering

**Files:**
- Create: `src/nuv/templates/main.py.tpl`
- Create: `src/nuv/templates/pyproject.toml.tpl`
- Create: `src/nuv/templates/readme.md.tpl`
- Create: `src/nuv/templates/test_main.py.tpl`
- Create: `src/nuv/templates/__init__.py` (empty)
- Modify: `src/nuv/commands/new.py`
- Modify: `tests/test_new.py`

**Step 1: Create the template files**

`src/nuv/templates/main.py.tpl`:
```
import argparse
import logging
import sys
from typing import Sequence

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

PROJECT_NAME = "$name"

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="TODO")
    parser.add_argument(
        "--log-level",
        default="WARNING",
        choices=("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"),
        help="Logging level (default: WARNING).",
    )
    return parser


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    return build_parser().parse_args(argv)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    logging.basicConfig(
        level=args.log_level,
        format="%(levelname)s %(name)s: %(message)s",
        stream=sys.stderr,
    )
    log.debug("Starting %s", PROJECT_NAME)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

`src/nuv/templates/pyproject.toml.tpl`:
```
[project]
name = "$name"
version = "0.1.0"
description = ""
readme = "README.md"
requires-python = ">=3.14"
dependencies = []

[dependency-groups]
dev = [
    "pytest>=8",
    "pytest-cov>=6",
    "ruff>=0.9",
    "ty>=0.0.1a1",
]

[tool.pytest.ini_options]
addopts = "--cov=$module_name --cov-report=term-missing --cov-fail-under=100"

[tool.ruff]
target-version = "py314"

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B", "SIM"]

[tool.coverage.run]
branch = true

[tool.coverage.report]
exclude_lines = ["if __name__ == .__main__.:"]
```

`src/nuv/templates/readme.md.tpl`:
```
# $name
```

`src/nuv/templates/test_main.py.tpl`:
```
from $module_name.main import main


def test_main_returns_zero() -> None:
    assert main([]) == 0
```

Wait — re the test template: for simple single-file projects (not packages), `main.py` is at root, not in a package. Update `test_main.py.tpl` to:

```
from main import main


def test_main_returns_zero() -> None:
    assert main([]) == 0
```

And the pyproject.toml coverage target `$module_name` should be `.` for a flat layout. Update:

```
addopts = "--cov=. --cov-report=term-missing --cov-fail-under=100"
```

**Step 2: Write failing tests for template rendering**

```python
from nuv.commands.new import render_template


def test_render_template_substitutes_name() -> None:
    result = render_template("readme.md.tpl", name="hello-world", module_name="hello_world")
    assert "hello-world" in result


def test_render_template_substitutes_module_name() -> None:
    result = render_template("pyproject.toml.tpl", name="hello-world", module_name="hello_world")
    assert "hello-world" in result


def test_render_template_unknown_raises() -> None:
    with pytest.raises(FileNotFoundError):
        render_template("nonexistent.tpl", name="x", module_name="x")
```

**Step 3: Run to verify they fail**

```bash
uv run pytest tests/test_new.py -k "render_template" -v
```

**Step 4: Implement `render_template`**

Add to `src/nuv/commands/new.py`:

```python
from string import Template


_TEMPLATES_DIR = Path(__file__).parent.parent / "templates"


def render_template(tpl_name: str, *, name: str, module_name: str) -> str:
    tpl_path = _TEMPLATES_DIR / tpl_name
    if not tpl_path.exists():
        raise FileNotFoundError(f"Template not found: {tpl_name}")
    return Template(tpl_path.read_text(encoding="utf-8")).substitute(
        name=name,
        module_name=module_name,
    )
```

**Step 5: Run tests to verify they pass**

```bash
uv run pytest tests/test_new.py -k "render_template" -v
```

**Step 6: Commit**

```bash
git add src/nuv/templates/ src/nuv/commands/new.py tests/test_new.py
git commit -m "feat: add template files and rendering"
```

---

### Task 5: File scaffolding

**Files:**
- Modify: `src/nuv/commands/new.py`
- Modify: `tests/test_new.py`

**Step 1: Write failing tests**

```python
from nuv.commands.new import scaffold_files


def test_scaffold_files_creates_expected_files(tmp_path: Path) -> None:
    target = tmp_path / "my-project"
    target.mkdir()
    scaffold_files(target, name="my-project", module_name="my_project")

    assert (target / "main.py").exists()
    assert (target / "pyproject.toml").exists()
    assert (target / "README.md").exists()
    assert (target / "tests" / "test_main.py").exists()
    assert (target / "tests" / "__init__.py").exists()


def test_scaffold_files_substitutes_name(tmp_path: Path) -> None:
    target = tmp_path / "my-project"
    target.mkdir()
    scaffold_files(target, name="my-project", module_name="my_project")
    assert "my-project" in (target / "README.md").read_text()


def test_scaffold_files_main_has_project_name(tmp_path: Path) -> None:
    target = tmp_path / "cool-tool"
    target.mkdir()
    scaffold_files(target, name="cool-tool", module_name="cool_tool")
    assert 'PROJECT_NAME = "cool-tool"' in (target / "main.py").read_text()
```

**Step 2: Run to verify they fail**

```bash
uv run pytest tests/test_new.py -k "scaffold_files" -v
```

**Step 3: Implement `scaffold_files`**

Add to `src/nuv/commands/new.py`:

```python
def scaffold_files(target: Path, *, name: str, module_name: str) -> None:
    vars = {"name": name, "module_name": module_name}

    (target / "main.py").write_text(
        render_template("main.py.tpl", **vars), encoding="utf-8"
    )
    (target / "pyproject.toml").write_text(
        render_template("pyproject.toml.tpl", **vars), encoding="utf-8"
    )
    (target / "README.md").write_text(
        render_template("readme.md.tpl", **vars), encoding="utf-8"
    )
    tests_dir = target / "tests"
    tests_dir.mkdir()
    (tests_dir / "__init__.py").write_text("", encoding="utf-8")
    (tests_dir / "test_main.py").write_text(
        render_template("test_main.py.tpl", **vars), encoding="utf-8"
    )
```

**Step 4: Run tests to verify they pass**

```bash
uv run pytest tests/test_new.py -k "scaffold_files" -v
```

**Step 5: Commit**

```bash
git add src/nuv/commands/new.py tests/test_new.py
git commit -m "feat: implement file scaffolding"
```

---

### Task 6: uv sync subprocess call

**Files:**
- Modify: `src/nuv/commands/new.py`
- Modify: `tests/test_new.py`

**Step 1: Write failing tests**

```python
import subprocess
from unittest.mock import patch, MagicMock
from nuv.commands.new import run_uv_sync


def test_run_uv_sync_calls_uv(tmp_path: Path) -> None:
    with patch("nuv.commands.new.shutil.which", return_value="/usr/bin/uv"), \
         patch("nuv.commands.new.subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0)
        run_uv_sync(tmp_path)
        mock_run.assert_called_once_with(
            ["uv", "sync"],
            cwd=tmp_path,
            check=False,
        )


def test_run_uv_sync_uv_not_found(tmp_path: Path) -> None:
    with patch("nuv.commands.new.shutil.which", return_value=None):
        with pytest.raises(RuntimeError, match="uv not found"):
            run_uv_sync(tmp_path)


def test_run_uv_sync_nonzero_exit(tmp_path: Path) -> None:
    with patch("nuv.commands.new.shutil.which", return_value="/usr/bin/uv"), \
         patch("nuv.commands.new.subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=1)
        with pytest.raises(RuntimeError, match="uv sync failed"):
            run_uv_sync(tmp_path)
```

**Step 2: Run to verify they fail**

```bash
uv run pytest tests/test_new.py -k "run_uv_sync" -v
```

**Step 3: Implement `run_uv_sync`**

Add to `src/nuv/commands/new.py`:

```python
import shutil
import subprocess


def run_uv_sync(target: Path) -> None:
    if shutil.which("uv") is None:
        raise RuntimeError("uv not found in PATH. Install uv: https://docs.astral.sh/uv/")
    result = subprocess.run(["uv", "sync"], cwd=target, check=False)
    if result.returncode != 0:
        raise RuntimeError(f"uv sync failed (exit {result.returncode})")
```

**Step 4: Run tests to verify they pass**

```bash
uv run pytest tests/test_new.py -k "run_uv_sync" -v
```

**Step 5: Commit**

```bash
git add src/nuv/commands/new.py tests/test_new.py
git commit -m "feat: add uv sync invocation"
```

---

### Task 7: Wire `run_new` end-to-end

**Files:**
- Modify: `src/nuv/commands/new.py`
- Modify: `tests/test_new.py`

**Step 1: Write failing end-to-end test**

```python
from nuv.commands.new import run_new


def test_run_new_success(tmp_path: Path) -> None:
    with patch("nuv.commands.new.shutil.which", return_value="/usr/bin/uv"), \
         patch("nuv.commands.new.subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0)
        result = run_new("cool-tool", at=str(tmp_path / "cool-tool"), cwd=tmp_path)
    assert result == 0
    assert (tmp_path / "cool-tool" / "main.py").exists()


def test_run_new_invalid_name(tmp_path: Path) -> None:
    result = run_new("bad name", cwd=tmp_path)
    assert result == 1


def test_run_new_existing_dir(tmp_path: Path) -> None:
    (tmp_path / "existing").mkdir()
    result = run_new("existing", cwd=tmp_path)
    assert result == 1


def test_run_new_uv_not_found(tmp_path: Path) -> None:
    with patch("nuv.commands.new.shutil.which", return_value=None):
        result = run_new("my-project", cwd=tmp_path)
    assert result == 1
```

**Step 2: Run to verify they fail**

```bash
uv run pytest tests/test_new.py -k "run_new" -v
```

**Step 3: Implement `run_new`**

Replace the stub `run_new` in `src/nuv/commands/new.py`:

```python
def run_new(name: str, *, at: str | None = None, cwd: Path | None = None) -> int:
    if cwd is None:
        cwd = Path.cwd()
    try:
        validated = validate_name(name)
        target = resolve_target(validated, at=at, cwd=cwd)
        module_name = validated.replace("-", "_")
        target.mkdir(parents=True)
        scaffold_files(target, name=validated, module_name=module_name)
        run_uv_sync(target)
    except (ValueError, RuntimeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    print(f"created {target}/")
    return 0
```

Add `import sys` at the top of `new.py`.

**Step 4: Run tests to verify they pass**

```bash
uv run pytest tests/test_new.py -k "run_new" -v
```

**Step 5: Commit**

```bash
git add src/nuv/commands/new.py tests/test_new.py
git commit -m "feat: wire run_new end-to-end"
```

---

### Task 8: CLI tests + full coverage sweep

**Files:**
- Modify: `tests/test_new.py`

We need the CLI `main()` and the `build_parser()` covered. Also ensure every branch in `new.py` is exercised.

**Step 1: Write CLI tests**

```python
from nuv.cli import main as cli_main


def test_cli_no_args_returns_1() -> None:
    assert cli_main([]) == 1


def test_cli_new_dispatches(tmp_path: Path) -> None:
    with patch("nuv.commands.new.shutil.which", return_value="/usr/bin/uv"), \
         patch("nuv.commands.new.subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0)
        result = cli_main(["new", "test-proj", "--at", str(tmp_path / "test-proj")])
    assert result == 0
```

**Step 2: Run full test suite with coverage**

```bash
uv run pytest --cov=nuv --cov-report=term-missing
```

Examine the missing lines report. Write targeted tests for any uncovered branches until coverage is 100%.

**Step 3: Run ruff and ty**

```bash
uv run ruff check src/ tests/
uv run ruff format --check src/ tests/
uv run ty check src/
```

Fix any issues found.

**Step 4: Run full suite one final time**

```bash
uv run pytest
```

Expected: all tests pass, coverage 100%.

**Step 5: Commit**

```bash
git add tests/test_new.py src/
git commit -m "test: achieve 100% coverage, fix lint and type errors"
```

---

### Task 9: Smoke-test a generated project

**This task is manual verification — no code to write.**

**Step 1: Run `nuv new` for real**

```bash
cd ~/personal
uv run --project ~/personal/nuv nuv new smoke-test
```

Or if installed via `uv tool install`:

```bash
nuv new smoke-test
```

**Step 2: Verify generated project**

```bash
cd smoke-test
uv run pytest          # should pass
uv run ruff check .    # should pass
uv run ty check        # should pass
```

Expected: all green, one test passing.

**Step 3: Commit final state**

```bash
cd ~/personal/nuv
git add .
git commit -m "chore: final state after smoke test"
```

---

## Quick Reference: Running Checks

All commands run from `~/personal/nuv`:

```bash
# Run tests with coverage
uv run pytest

# Lint
uv run ruff check src/ tests/

# Format check
uv run ruff format --check src/ tests/

# Type check
uv run ty check src/

# All at once
uv run ruff check src/ tests/ && uv run ruff format --check src/ tests/ && uv run ty check src/ && uv run pytest
```
