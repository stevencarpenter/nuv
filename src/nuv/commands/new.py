import re
import shutil
import subprocess
from pathlib import Path
from string import Template


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


_TEMPLATES_DIR = Path(__file__).parent.parent / "templates"


def render_template(tpl_name: str, *, name: str, module_name: str) -> str:
    tpl_path = _TEMPLATES_DIR / tpl_name
    if not tpl_path.exists():
        raise FileNotFoundError(f"Template not found: {tpl_name}")
    return Template(tpl_path.read_text(encoding="utf-8")).substitute(
        name=name,
        module_name=module_name,
    )


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


def run_uv_sync(target: Path) -> None:
    if shutil.which("uv") is None:
        raise RuntimeError("uv not found in PATH. Install uv: https://docs.astral.sh/uv/")
    result = subprocess.run(["uv", "sync"], cwd=target, check=False)
    if result.returncode != 0:
        raise RuntimeError(f"uv sync failed (exit {result.returncode})")


def resolve_target(name: str, *, at: str | None, cwd: Path) -> Path:
    target = Path(at) if at else cwd / name
    if target.exists():
        raise ValueError(f"Directory already exists: {target}")
    return target


def run_new(name: str, *, at: str | None = None) -> int:
    return 0
