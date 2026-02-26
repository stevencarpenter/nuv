import logging
import re
import shutil
import subprocess
from pathlib import Path

log = logging.getLogger(__name__)


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


_TEMPLATES_ROOT = Path(__file__).parent.parent / "templates"
DEFAULT_PYTHON_VERSION = "3.14"


def render_template(
    tpl_name: str,
    *,
    archetype: str = "script",
    name: str,
    module_name: str,
    python_version: str = DEFAULT_PYTHON_VERSION,
) -> str:
    tpl_path = _TEMPLATES_ROOT / archetype / tpl_name
    if not tpl_path.exists():
        raise FileNotFoundError(f"Template not found: {archetype}/{tpl_name}")
    return tpl_path.read_text(encoding="utf-8").format(
        name=name,
        module_name=module_name,
        python_version=python_version,
        python_version_nodot=python_version.replace(".", ""),
    )


def scaffold_files(
    target: Path,
    *,
    name: str,
    module_name: str,
    archetype: str = "script",
    python_version: str = DEFAULT_PYTHON_VERSION,
) -> None:
    template_vars = {
        "name": name,
        "module_name": module_name,
        "archetype": archetype,
        "python_version": python_version,
    }

    (target / ".python-version").write_text(f"{python_version}\n", encoding="utf-8")
    (target / ".gitignore").write_text(render_template("gitignore.tpl", **template_vars), encoding="utf-8")
    (target / "main.py").write_text(render_template("main.py.tpl", **template_vars), encoding="utf-8")
    (target / "pyproject.toml").write_text(render_template("pyproject.toml.tpl", **template_vars), encoding="utf-8")
    (target / "README.md").write_text(render_template("readme.md.tpl", **template_vars), encoding="utf-8")
    tests_dir = target / "tests"
    tests_dir.mkdir()
    (tests_dir / "__init__.py").write_text("", encoding="utf-8")
    (tests_dir / "test_main.py").write_text(render_template("test_main.py.tpl", **template_vars), encoding="utf-8")


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


def run_new(
    name: str,
    *,
    at: str | None = None,
    cwd: Path | None = None,
    archetype: str = "script",
    python_version: str = DEFAULT_PYTHON_VERSION,
) -> int:
    if cwd is None:
        cwd = Path.cwd()
    try:
        validated = validate_name(name)
        target = resolve_target(validated, at=at, cwd=cwd)
        module_name = validated.replace("-", "_")
        target.mkdir(parents=True)
        scaffold_files(
            target,
            name=validated,
            module_name=module_name,
            archetype=archetype,
            python_version=python_version,
        )
        run_uv_sync(target)
    except (ValueError, RuntimeError, FileNotFoundError) as exc:
        log.error("%s", exc)
        return 1
    log.info("created %s/", target)
    return 0
