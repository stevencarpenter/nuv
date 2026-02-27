import logging
import re
import shutil
import subprocess
from pathlib import Path

log = logging.getLogger(__name__)

INSTALL_MODES = ("editable", "none", "command-only")


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


def validate_python_version(version: str) -> str:
    if not re.fullmatch(r"\d+\.\d+", version):
        raise ValueError(f"Python version must be MAJOR.MINOR (e.g. 3.14), got: {version!r}")
    return version


def validate_install_mode(mode: str) -> str:
    if mode not in INSTALL_MODES:
        raise ValueError(f"Install mode must be one of {INSTALL_MODES}, got: {mode!r}")
    return mode


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


def write_with_trailing_newline(path: Path, content: str) -> None:
    normalized = content if content.endswith("\n") else f"{content}\n"
    path.write_text(normalized, encoding="utf-8")


def scaffold_files(
    target: Path,
    *,
    name: str,
    module_name: str,
    archetype: str = "script",
    python_version: str = DEFAULT_PYTHON_VERSION,
) -> None:
    validate_python_version(python_version)
    template_vars = {
        "name": name,
        "module_name": module_name,
        "archetype": archetype,
        "python_version": python_version,
    }

    write_with_trailing_newline(target / ".python-version", python_version)
    write_with_trailing_newline(target / ".gitignore", render_template("gitignore.tpl", **template_vars))
    write_with_trailing_newline(target / "_logging.py", render_template("_logging.py.tpl", **template_vars))
    write_with_trailing_newline(target / "main.py", render_template("main.py.tpl", **template_vars))
    write_with_trailing_newline(target / "pyproject.toml", render_template("pyproject.toml.tpl", **template_vars))
    write_with_trailing_newline(target / "README.md", render_template("readme.md.tpl", **template_vars))
    tests_dir = target / "tests"
    tests_dir.mkdir()
    write_with_trailing_newline(tests_dir / "__init__.py", "")
    write_with_trailing_newline(tests_dir / "test_main.py", render_template("test_main.py.tpl", **template_vars))


def run_uv_sync(target: Path) -> None:
    if shutil.which("uv") is None:
        raise RuntimeError("uv not found in PATH. Install uv: https://docs.astral.sh/uv/")
    result = subprocess.run(["uv", "sync"], cwd=target, check=False)
    if result.returncode != 0:
        raise RuntimeError(f"uv sync failed (exit {result.returncode})")


def build_tool_install_command(target: Path) -> list[str]:
    return ["uv", "tool", "install", "--editable", str(target)]


def run_tool_install(target: Path, *, mode: str) -> None:
    validated_mode = validate_install_mode(mode)
    if validated_mode == "none":
        return

    command = build_tool_install_command(target)
    if validated_mode == "command-only":
        log.warning("Run this to install the generated tool:")
        log.warning("%s", " ".join(command))
        return

    if shutil.which("uv") is None:
        raise RuntimeError("uv not found in PATH. Install uv: https://docs.astral.sh/uv/")
    result = subprocess.run(command, cwd=target, check=False)
    if result.returncode != 0:
        raise RuntimeError(f"uv tool install failed (exit {result.returncode})")
    log.info("installed tool in editable mode at %s", target)


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
    install_mode: str = "command-only",
    keep_on_failure: bool = False,
) -> int:
    if cwd is None:
        cwd = Path.cwd()
    target: Path | None = None
    created_target = False
    try:
        validated = validate_name(name)
        target = resolve_target(validated, at=at, cwd=cwd)
        module_name = validated.replace("-", "_")
        target.mkdir(parents=True)
        created_target = True
        scaffold_files(
            target,
            name=validated,
            module_name=module_name,
            archetype=archetype,
            python_version=python_version,
        )
        run_uv_sync(target)
        run_tool_install(target, mode=install_mode)
    except (ValueError, RuntimeError, FileNotFoundError) as exc:
        if created_target and target is not None and not keep_on_failure:
            shutil.rmtree(target, ignore_errors=True)
        log.error("%s", exc)
        return 1
    log.info("created %s/", target)
    return 0
