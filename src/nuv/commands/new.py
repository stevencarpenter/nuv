import json
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
DEFAULT_PYTHON_VERSIONS = {"script": "3.14", "spark": "3.13", "fastapi": "3.14"}


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


def generate_jupyter_notebook(name: str, *, python_version: str = DEFAULT_PYTHON_VERSION) -> str:
    """Build a starter Jupyter notebook as JSON.

    Generated programmatically instead of via .tpl because .ipynb JSON
    braces conflict with str.format() placeholders.
    """

    def _code_cell(source: list[str]) -> dict:
        return {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": source,
        }

    def _md_cell(source: list[str]) -> dict:
        return {
            "cell_type": "markdown",
            "metadata": {},
            "source": source,
        }

    cells = [
        _md_cell([f"# {name} — Exploration Notebook"]),
        _code_cell(
            [
                "from pyspark.sql import SparkSession\n",
                "\n",
                f'spark = SparkSession.builder.master("local[*]").appName("{name}").getOrCreate()\n',
                "spark",
            ]
        ),
        _md_cell(["## Create a sample DataFrame"]),
        _code_cell(
            [
                'data = [("alice", 1), ("bob", 2), ("charlie", 3)]\n',
                'df = spark.createDataFrame(data, ["name", "value"])\n',
                "df.show()",
            ]
        ),
        _md_cell(["## Filter"]),
        _code_cell(
            [
                "filtered = df.filter(df.value > 1)\n",
                "filtered.show()",
            ]
        ),
        _md_cell(["## Group By"]),
        _code_cell(
            [
                'grouped = df.groupBy("name").sum("value")\n',
                "grouped.show()",
            ]
        ),
    ]

    notebook = {
        "cells": cells,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3",
            },
            "language_info": {
                "name": "python",
                "version": f"{python_version}.0",
            },
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    return json.dumps(notebook, indent=1) + "\n"


VALID_ARCHETYPES = ("script", "spark", "fastapi")


def scaffold_files(
    target: Path,
    *,
    name: str,
    module_name: str,
    archetype: str = "script",
    python_version: str = DEFAULT_PYTHON_VERSION,
) -> None:
    if archetype not in VALID_ARCHETYPES:
        raise ValueError(f"Unknown archetype: {archetype!r}")
    validate_python_version(python_version)
    template_vars = {
        "name": name,
        "module_name": module_name,
        "archetype": archetype,
        "python_version": python_version,
    }

    # Shared files
    write_with_trailing_newline(target / ".python-version", python_version)
    write_with_trailing_newline(target / ".gitignore", render_template("gitignore.tpl", **template_vars))
    write_with_trailing_newline(target / "pyproject.toml", render_template("pyproject.toml.tpl", **template_vars))
    write_with_trailing_newline(target / "README.md", render_template("readme.md.tpl", **template_vars))
    write_with_trailing_newline(target / "main.py", render_template("main.py.tpl", **template_vars))

    tests_dir = target / "tests"
    tests_dir.mkdir()
    write_with_trailing_newline(tests_dir / "__init__.py", "")

    if archetype == "script":
        write_with_trailing_newline(target / "_logging.py", render_template("_logging.py.tpl", **template_vars))
        write_with_trailing_newline(tests_dir / "test_main.py", render_template("test_main.py.tpl", **template_vars))
    elif archetype == "spark":
        _scaffold_spark(target, template_vars=template_vars, name=name, module_name=module_name)
    else:  # fastapi — validated by VALID_ARCHETYPES above
        _scaffold_fastapi(target, template_vars=template_vars, name=name, module_name=module_name)


def _scaffold_spark(
    target: Path,
    *,
    template_vars: dict[str, str],
    name: str,
    module_name: str,
) -> None:
    # src/<module_name>/ package
    pkg_dir = target / "src" / module_name
    pkg_dir.mkdir(parents=True)
    write_with_trailing_newline(pkg_dir / "__init__.py", render_template("init.py.tpl", **template_vars))
    write_with_trailing_newline(pkg_dir / "_logging.py", render_template("_logging.py.tpl", **template_vars))
    write_with_trailing_newline(pkg_dir / "config.py", render_template("config.py.tpl", **template_vars))
    write_with_trailing_newline(pkg_dir / "session.py", render_template("session.py.tpl", **template_vars))

    # src/<module_name>/jobs/
    jobs_dir = pkg_dir / "jobs"
    jobs_dir.mkdir()
    write_with_trailing_newline(jobs_dir / "__init__.py", render_template("jobs_init.py.tpl", **template_vars))
    write_with_trailing_newline(jobs_dir / "example.py", render_template("example_job.py.tpl", **template_vars))

    # tests/
    tests_dir = target / "tests"
    write_with_trailing_newline(tests_dir / "conftest.py", render_template("conftest.py.tpl", **template_vars))
    write_with_trailing_newline(tests_dir / "test_example.py", render_template("test_example.py.tpl", **template_vars))

    # notebooks/
    notebooks_dir = target / "notebooks"
    notebooks_dir.mkdir()
    write_with_trailing_newline(notebooks_dir / "explore.ipynb", generate_jupyter_notebook(name, python_version=template_vars["python_version"]))
    write_with_trailing_newline(notebooks_dir / "explore_marimo.py", render_template("explore_marimo.py.tpl", **template_vars))


def _scaffold_fastapi(
    target: Path,
    *,
    template_vars: dict[str, str],
    name: str,
    module_name: str,
) -> None:
    # src/<module_name>/ package
    pkg_dir = target / "src" / module_name
    pkg_dir.mkdir(parents=True)
    write_with_trailing_newline(pkg_dir / "__init__.py", render_template("init.py.tpl", **template_vars))
    write_with_trailing_newline(pkg_dir / "app.py", render_template("app.py.tpl", **template_vars))
    write_with_trailing_newline(pkg_dir / "config.py", render_template("config.py.tpl", **template_vars))
    write_with_trailing_newline(pkg_dir / "_logging.py", render_template("_logging.py.tpl", **template_vars))
    write_with_trailing_newline(pkg_dir / "dependencies.py", render_template("dependencies.py.tpl", **template_vars))

    # src/<module_name>/routes/
    routes_dir = pkg_dir / "routes"
    routes_dir.mkdir()
    write_with_trailing_newline(routes_dir / "__init__.py", render_template("routes_init.py.tpl", **template_vars))
    write_with_trailing_newline(routes_dir / "health.py", render_template("health.py.tpl", **template_vars))

    # tests/
    tests_dir = target / "tests"
    write_with_trailing_newline(tests_dir / "conftest.py", render_template("conftest.py.tpl", **template_vars))
    write_with_trailing_newline(tests_dir / "test_health.py", render_template("test_health.py.tpl", **template_vars))

    # Docker
    write_with_trailing_newline(target / "Dockerfile", render_template("dockerfile.tpl", **template_vars))
    write_with_trailing_newline(target / ".dockerignore", render_template("dockerignore.tpl", **template_vars))


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
    python_version: str | None = None,
    install_mode: str = "command-only",
    keep_on_failure: bool = False,
) -> int:
    if python_version is None:
        python_version = DEFAULT_PYTHON_VERSIONS.get(archetype, DEFAULT_PYTHON_VERSION)
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
