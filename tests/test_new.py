from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from nuv.cli import main as cli_main
from nuv.commands.new import (
    DEFAULT_PYTHON_VERSION,
    DEFAULT_PYTHON_VERSIONS,
    build_tool_install_command,
    generate_jupyter_notebook,
    render_template,
    resolve_target,
    run_new,
    run_tool_install,
    run_uv_sync,
    scaffold_files,
    validate_install_mode,
    validate_name,
    validate_python_version,
)


def test_no_command_returns_1() -> None:
    assert cli_main([]) == 1


# ---------------------------------------------------------------------------
# validate_name
# ---------------------------------------------------------------------------


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


# ---------------------------------------------------------------------------
# validate_python_version
# ---------------------------------------------------------------------------


def test_validate_python_version_valid() -> None:
    assert validate_python_version("3.14") == "3.14"


def test_validate_python_version_invalid_patch() -> None:
    with pytest.raises(ValueError, match="MAJOR.MINOR"):
        validate_python_version("3.14.1")


def test_validate_python_version_invalid_bare() -> None:
    with pytest.raises(ValueError, match="MAJOR.MINOR"):
        validate_python_version("3")


# ---------------------------------------------------------------------------
# install mode
# ---------------------------------------------------------------------------


def test_validate_install_mode_valid() -> None:
    assert validate_install_mode("editable") == "editable"


def test_validate_install_mode_invalid() -> None:
    with pytest.raises(ValueError, match="Install mode"):
        validate_install_mode("bad")


def test_build_tool_install_command(tmp_path: Path) -> None:
    target = tmp_path / "my-project"
    assert build_tool_install_command(target) == ["uv", "tool", "install", "--editable", str(target)]


def test_run_tool_install_none(tmp_path: Path) -> None:
    run_tool_install(tmp_path, mode="none")


def test_run_tool_install_command_only(tmp_path: Path, caplog: pytest.LogCaptureFixture) -> None:
    with caplog.at_level("INFO", logger="nuv.commands.new"):
        run_tool_install(tmp_path, mode="command-only")
    assert "uv tool install --editable" in caplog.text


def test_run_tool_install_editable_calls_uv(tmp_path: Path) -> None:
    with (
        patch("nuv.commands.new.shutil.which", return_value="/usr/bin/uv"),
        patch("nuv.commands.new.subprocess.run") as mock_run,
    ):
        mock_run.return_value = MagicMock(returncode=0)
        run_tool_install(tmp_path, mode="editable")
    mock_run.assert_called_once_with(
        ["uv", "tool", "install", "--editable", str(tmp_path)],
        cwd=tmp_path,
        check=False,
    )


def test_run_tool_install_editable_logs_success(tmp_path: Path, caplog: pytest.LogCaptureFixture) -> None:
    with (
        patch("nuv.commands.new.shutil.which", return_value="/usr/bin/uv"),
        patch("nuv.commands.new.subprocess.run") as mock_run,
        caplog.at_level("INFO", logger="nuv.commands.new"),
    ):
        mock_run.return_value = MagicMock(returncode=0)
        run_tool_install(tmp_path, mode="editable")
    assert "installed tool in editable mode at" in caplog.text


def test_run_tool_install_editable_uv_not_found(tmp_path: Path) -> None:
    with (
        patch("nuv.commands.new.shutil.which", return_value=None),
        pytest.raises(RuntimeError, match="uv not found"),
    ):
        run_tool_install(tmp_path, mode="editable")


def test_run_tool_install_editable_nonzero_exit(tmp_path: Path) -> None:
    with (
        patch("nuv.commands.new.shutil.which", return_value="/usr/bin/uv"),
        patch("nuv.commands.new.subprocess.run") as mock_run,
        pytest.raises(RuntimeError, match="uv tool install failed"),
    ):
        mock_run.return_value = MagicMock(returncode=1)
        run_tool_install(tmp_path, mode="editable")


# ---------------------------------------------------------------------------
# resolve_target
# ---------------------------------------------------------------------------


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


# ---------------------------------------------------------------------------
# render_template
# ---------------------------------------------------------------------------


def test_render_template_substitutes_name() -> None:
    result = render_template("readme.md.tpl", name="hello-world", module_name="hello_world")
    assert "hello-world" in result


def test_render_template_pyproject_uses_name() -> None:
    result = render_template("pyproject.toml.tpl", name="hello-world", module_name="hello_world")
    assert "hello-world" in result


def test_render_template_unknown_raises() -> None:
    with pytest.raises(FileNotFoundError):
        render_template("nonexistent.tpl", name="x", module_name="x")


# ---------------------------------------------------------------------------
# generate_jupyter_notebook
# ---------------------------------------------------------------------------


def test_generate_jupyter_notebook_valid_json() -> None:
    import json

    result = generate_jupyter_notebook("my-spark-app")
    notebook = json.loads(result)
    assert notebook["nbformat"] == 4
    assert len(notebook["cells"]) == 8
    assert notebook["cells"][0]["cell_type"] == "markdown"
    assert "my-spark-app" in notebook["cells"][0]["source"][0]


def test_generate_jupyter_notebook_contains_spark_session() -> None:
    result = generate_jupyter_notebook("my-spark-app")
    assert "SparkSession" in result
    assert "my-spark-app" in result


def test_generate_jupyter_notebook_python_version_default() -> None:
    import json

    result = generate_jupyter_notebook("my-spark-app")
    notebook = json.loads(result)
    assert notebook["metadata"]["language_info"]["version"] == f"{DEFAULT_PYTHON_VERSION}.0"


def test_generate_jupyter_notebook_python_version_custom() -> None:
    import json

    result = generate_jupyter_notebook("my-spark-app", python_version="3.13")
    notebook = json.loads(result)
    assert notebook["metadata"]["language_info"]["version"] == "3.13.0"


# ---------------------------------------------------------------------------
# scaffold_files
# ---------------------------------------------------------------------------


def test_scaffold_files_creates_expected_files(tmp_path: Path) -> None:
    target = tmp_path / "my-project"
    target.mkdir()
    scaffold_files(target, name="my-project", module_name="my_project")

    assert (target / ".python-version").exists()
    assert (target / ".gitignore").exists()
    assert (target / "_logging.py").exists()
    assert (target / "main.py").exists()
    assert (target / "pyproject.toml").exists()
    assert (target / "README.md").exists()
    assert (target / "tests" / "test_main.py").exists()
    assert (target / "tests" / "__init__.py").exists()


def test_scaffold_files_python_version_content(tmp_path: Path) -> None:
    target = tmp_path / "my-project"
    target.mkdir()
    scaffold_files(target, name="my-project", module_name="my_project")
    assert (target / ".python-version").read_text().strip() == DEFAULT_PYTHON_VERSION


def test_scaffold_files_gitignore_includes_common_dev_tooling(tmp_path: Path) -> None:
    target = tmp_path / "my-project"
    target.mkdir()
    scaffold_files(target, name="my-project", module_name="my_project")
    content = (target / ".gitignore").read_text()

    expected_entries = [
        ".idea/",
        "*.iml",
        ".vscode/",
        ".DS_Store",
        ".directory",
        "*.swp",
        "*.swo",
        "*~",
        ".claude/",
        ".codex/",
        ".copilot/",
        ".amp/",
        ".opencode/",
        ".venv/",
        "__pycache__/",
        "*.pyc",
        ".pytest_cache/",
        "htmlcov/",
        "dist/",
        "*.egg-info/",
        ".uv/",
        ".uvx/",
        ".ruff_cache/",
    ]

    for entry in expected_entries:
        assert entry in content


def test_scaffold_files_custom_python_version(tmp_path: Path) -> None:
    target = tmp_path / "my-project"
    target.mkdir()
    scaffold_files(target, name="my-project", module_name="my_project", python_version="3.13")
    assert (target / ".python-version").read_text().strip() == "3.13"
    pyproject = (target / "pyproject.toml").read_text()
    assert ">=3.13" in pyproject
    assert "py313" in pyproject
    assert "[project.scripts]" in pyproject
    assert 'build-backend = "hatchling.build"' in pyproject
    assert "setuptools" not in pyproject


def test_scaffold_files_invalid_python_version(tmp_path: Path) -> None:
    target = tmp_path / "my-project"
    target.mkdir()
    with pytest.raises(ValueError, match="MAJOR.MINOR"):
        scaffold_files(target, name="my-project", module_name="my_project", python_version="3.14.1")


def test_scaffold_files_substitutes_name(tmp_path: Path) -> None:
    target = tmp_path / "my-project"
    target.mkdir()
    scaffold_files(target, name="my-project", module_name="my_project")
    assert "my-project" in (target / "README.md").read_text()


def test_scaffold_files_logging_module_created(tmp_path: Path) -> None:
    target = tmp_path / "my-project"
    target.mkdir()
    scaffold_files(target, name="my-project", module_name="my_project")
    content = (target / "_logging.py").read_text()
    assert "LOG_FORMAT" in content
    assert "def configure(" in content


def test_scaffold_files_main_has_project_name(tmp_path: Path) -> None:
    target = tmp_path / "cool-tool"
    target.mkdir()
    scaffold_files(target, name="cool-tool", module_name="cool_tool")
    assert 'PROJECT_NAME = "cool-tool"' in (target / "main.py").read_text()


def test_scaffold_files_end_with_trailing_newline(tmp_path: Path) -> None:
    target = tmp_path / "my-project"
    target.mkdir()
    scaffold_files(target, name="my-project", module_name="my_project")

    generated_files = [
        ".python-version",
        ".gitignore",
        "_logging.py",
        "main.py",
        "pyproject.toml",
        "README.md",
        "tests/__init__.py",
        "tests/test_main.py",
    ]

    for rel_path in generated_files:
        content = (target / rel_path).read_text()
        assert content.endswith("\n"), f"Expected trailing newline in {rel_path}"


def test_scaffold_files_unknown_archetype_raises(tmp_path: Path) -> None:
    """An unrecognised archetype raises ValueError."""
    target = tmp_path / "my-project"
    target.mkdir()
    with pytest.raises(ValueError, match="Unknown archetype"):
        scaffold_files(target, name="my-project", module_name="my_project", archetype="unknown")


# ---------------------------------------------------------------------------
# run_uv_sync
# ---------------------------------------------------------------------------


def test_run_uv_sync_calls_uv(tmp_path: Path) -> None:
    with (
        patch("nuv.commands.new.shutil.which", return_value="/usr/bin/uv"),
        patch("nuv.commands.new.subprocess.run") as mock_run,
    ):
        mock_run.return_value = MagicMock(returncode=0)
        run_uv_sync(tmp_path)
        mock_run.assert_called_once_with(
            ["uv", "sync"],
            cwd=tmp_path,
            check=False,
        )


def test_run_uv_sync_uv_not_found(tmp_path: Path) -> None:
    with (
        patch("nuv.commands.new.shutil.which", return_value=None),
        pytest.raises(RuntimeError, match="uv not found"),
    ):
        run_uv_sync(tmp_path)


def test_run_uv_sync_nonzero_exit(tmp_path: Path) -> None:
    with (
        patch("nuv.commands.new.shutil.which", return_value="/usr/bin/uv"),
        patch("nuv.commands.new.subprocess.run") as mock_run,
        pytest.raises(RuntimeError, match="uv sync failed"),
    ):
        mock_run.return_value = MagicMock(returncode=1)
        run_uv_sync(tmp_path)


# ---------------------------------------------------------------------------
# run_new
# ---------------------------------------------------------------------------


def test_run_new_success(tmp_path: Path) -> None:
    with (
        patch("nuv.commands.new.shutil.which", return_value="/usr/bin/uv"),
        patch("nuv.commands.new.subprocess.run") as mock_run,
    ):
        mock_run.return_value = MagicMock(returncode=0)
        result = run_new("cool-tool", at=str(tmp_path / "cool-tool"), cwd=tmp_path)
    assert result == 0
    assert (tmp_path / "cool-tool" / "main.py").exists()
    mock_run.assert_called_once_with(["uv", "sync"], cwd=tmp_path / "cool-tool", check=False)


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
    assert not (tmp_path / "my-project").exists()


def test_run_new_uv_not_found_keep_on_failure(tmp_path: Path) -> None:
    with patch("nuv.commands.new.shutil.which", return_value=None):
        result = run_new("my-project", cwd=tmp_path, keep_on_failure=True)
    assert result == 1
    assert (tmp_path / "my-project").exists()


def test_run_new_missing_template(tmp_path: Path) -> None:
    with patch(
        "nuv.commands.new.scaffold_files",
        side_effect=FileNotFoundError("template not found"),
    ):
        result = run_new("my-project", cwd=tmp_path)
    assert result == 1


# ---------------------------------------------------------------------------
# archetype-aware default Python versions
# ---------------------------------------------------------------------------


def test_default_python_versions_script() -> None:
    assert DEFAULT_PYTHON_VERSIONS["script"] == "3.14"


def test_default_python_versions_spark() -> None:
    assert DEFAULT_PYTHON_VERSIONS["spark"] == "3.13"


def test_run_new_spark_uses_default_python_313(tmp_path: Path) -> None:
    with (
        patch("nuv.commands.new.shutil.which", return_value="/usr/bin/uv"),
        patch("nuv.commands.new.subprocess.run") as mock_run,
        patch("nuv.commands.new.scaffold_files") as mock_scaffold,
    ):
        mock_run.return_value = MagicMock(returncode=0)
        result = run_new("my-spark-app", at=str(tmp_path / "my-spark-app"), cwd=tmp_path, archetype="spark")
    assert result == 0
    mock_scaffold.assert_called_once()
    call_kwargs = mock_scaffold.call_args[1]
    assert call_kwargs["python_version"] == "3.13"
    assert call_kwargs["archetype"] == "spark"


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def test_cli_no_args_returns_1() -> None:
    assert cli_main([]) == 1


def test_cli_new_dispatches(tmp_path: Path) -> None:
    with (
        patch("nuv.commands.new.shutil.which", return_value="/usr/bin/uv"),
        patch("nuv.commands.new.subprocess.run") as mock_run,
    ):
        mock_run.return_value = MagicMock(returncode=0)
        result = cli_main(["new", "test-proj", "--at", str(tmp_path / "test-proj")])
    assert result == 0
    mock_run.assert_called_once_with(["uv", "sync"], cwd=tmp_path / "test-proj", check=False)


def test_cli_new_default_install_logs_command(tmp_path: Path, caplog: pytest.LogCaptureFixture) -> None:
    with (
        patch("nuv.commands.new.shutil.which", return_value="/usr/bin/uv"),
        patch("nuv.commands.new.subprocess.run") as mock_run,
        caplog.at_level("WARNING", logger="nuv.commands.new"),
    ):
        mock_run.return_value = MagicMock(returncode=0)
        result = cli_main(["new", "test-proj", "--at", str(tmp_path / "test-proj")])
    assert result == 0
    assert "uv tool install --editable" in caplog.text


def test_cli_invalid_archetype_rejected() -> None:
    with pytest.raises(SystemExit) as exc_info:
        cli_main(["new", "my-app", "--archetype", "invalid"])
    assert exc_info.value.code == 2


def test_cli_invalid_python_version_rejected() -> None:
    with pytest.raises(SystemExit) as exc_info:
        cli_main(["new", "my-app", "--python-version", "3.14.1"])
    assert exc_info.value.code == 2


def test_cli_python_version_passed_through(tmp_path: Path) -> None:
    with (
        patch("nuv.commands.new.shutil.which", return_value="/usr/bin/uv"),
        patch("nuv.commands.new.subprocess.run") as mock_run,
    ):
        mock_run.return_value = MagicMock(returncode=0)
        result = cli_main(["new", "test-proj", "--at", str(tmp_path / "test-proj"), "--python-version", "3.13"])
    assert result == 0
    assert (tmp_path / "test-proj" / ".python-version").read_text().strip() == "3.13"


def test_cli_invalid_install_mode_rejected() -> None:
    with pytest.raises(SystemExit) as exc_info:
        cli_main(["new", "my-app", "--install", "bad"])
    assert exc_info.value.code == 2


def test_run_new_install_none_only_sync(tmp_path: Path) -> None:
    with (
        patch("nuv.commands.new.shutil.which", return_value="/usr/bin/uv"),
        patch("nuv.commands.new.subprocess.run") as mock_run,
    ):
        mock_run.return_value = MagicMock(returncode=0)
        result = run_new("cool-tool", at=str(tmp_path / "cool-tool"), cwd=tmp_path, install_mode="none")
    assert result == 0
    mock_run.assert_called_once_with(["uv", "sync"], cwd=tmp_path / "cool-tool", check=False)


def test_cli_install_command_only(tmp_path: Path, caplog: pytest.LogCaptureFixture) -> None:
    with (
        patch("nuv.commands.new.shutil.which", return_value="/usr/bin/uv"),
        patch("nuv.commands.new.subprocess.run") as mock_run,
    ):
        mock_run.return_value = MagicMock(returncode=0)
        with caplog.at_level("INFO", logger="nuv.commands.new"):
            result = cli_main(["--log-level", "INFO", "new", "test-proj", "--at", str(tmp_path / "test-proj"), "--install", "command-only"])
    assert result == 0
    mock_run.assert_called_once_with(["uv", "sync"], cwd=tmp_path / "test-proj", check=False)
    assert "uv tool install --editable" in caplog.text


def test_cli_new_keep_on_failure_flag(tmp_path: Path) -> None:
    with patch("nuv.commands.new.shutil.which", return_value=None):
        result = cli_main(["new", "my-project", "--at", str(tmp_path / "my-project"), "--keep-on-failure"])
    assert result == 1
    assert (tmp_path / "my-project").exists()


def test_cli_new_unexpected_error_returns_1(capsys: pytest.CaptureFixture[str]) -> None:
    with (
        patch("nuv.commands.new.run_new", side_effect=Exception("boom")),
        pytest.raises(SystemExit) as exc_info,
    ):
        cli_main(["new", "my-project"])
    assert exc_info.value.code == 1
    assert "ERROR unexpected failure" in capsys.readouterr().err


# ---------------------------------------------------------------------------
# spark archetype — scaffold_files
# ---------------------------------------------------------------------------


def test_scaffold_files_spark_creates_expected_files(tmp_path: Path) -> None:
    target = tmp_path / "my-spark-app"
    target.mkdir()
    scaffold_files(target, name="my-spark-app", module_name="my_spark_app", archetype="spark", python_version="3.13")

    assert (target / ".python-version").exists()
    assert (target / ".gitignore").exists()
    assert (target / "main.py").exists()
    assert (target / "pyproject.toml").exists()
    assert (target / "README.md").exists()
    assert (target / "src" / "my_spark_app" / "__init__.py").exists()
    assert (target / "src" / "my_spark_app" / "_logging.py").exists()
    assert (target / "src" / "my_spark_app" / "config.py").exists()
    assert (target / "src" / "my_spark_app" / "session.py").exists()
    assert (target / "src" / "my_spark_app" / "jobs" / "__init__.py").exists()
    assert (target / "src" / "my_spark_app" / "jobs" / "example.py").exists()
    assert (target / "tests" / "__init__.py").exists()
    assert (target / "tests" / "conftest.py").exists()
    assert (target / "tests" / "test_example.py").exists()
    assert (target / "notebooks" / "explore.ipynb").exists()
    assert (target / "notebooks" / "explore_marimo.py").exists()


def test_scaffold_files_spark_python_version_content(tmp_path: Path) -> None:
    target = tmp_path / "my-spark-app"
    target.mkdir()
    scaffold_files(target, name="my-spark-app", module_name="my_spark_app", archetype="spark", python_version="3.13")
    assert (target / ".python-version").read_text().strip() == "3.13"


def test_scaffold_files_spark_pyproject_has_pyspark(tmp_path: Path) -> None:
    target = tmp_path / "my-spark-app"
    target.mkdir()
    scaffold_files(target, name="my-spark-app", module_name="my_spark_app", archetype="spark", python_version="3.13")
    pyproject = (target / "pyproject.toml").read_text()
    assert "pyspark>=4.1.1,<5" in pyproject
    assert "chispa>=0.12.0" in pyproject
    assert "jupyterlab>=4.5.7" in pyproject
    assert "marimo>=0.23.4" in pyproject
    assert "py313" in pyproject
    assert 'packages = ["src/my_spark_app"]' in pyproject
    assert 'build-backend = "hatchling.build"' in pyproject


def test_scaffold_files_spark_gitignore_has_spark_entries(tmp_path: Path) -> None:
    target = tmp_path / "my-spark-app"
    target.mkdir()
    scaffold_files(target, name="my-spark-app", module_name="my_spark_app", archetype="spark", python_version="3.13")
    content = (target / ".gitignore").read_text()
    assert "derby.log" in content
    assert "metastore_db/" in content
    assert "spark-warehouse/" in content
    assert ".ipynb_checkpoints/" in content


def test_scaffold_files_spark_main_imports_package(tmp_path: Path) -> None:
    target = tmp_path / "my-spark-app"
    target.mkdir()
    scaffold_files(target, name="my-spark-app", module_name="my_spark_app", archetype="spark", python_version="3.13")
    main_content = (target / "main.py").read_text()
    assert "from my_spark_app._logging import configure" in main_content
    assert "from my_spark_app.config import resolve_params" in main_content
    assert "from my_spark_app.session import create_spark_session" in main_content


def test_scaffold_files_spark_test_uses_chispa(tmp_path: Path) -> None:
    target = tmp_path / "my-spark-app"
    target.mkdir()
    scaffold_files(target, name="my-spark-app", module_name="my_spark_app", archetype="spark", python_version="3.13")
    test_content = (target / "tests" / "test_example.py").read_text()
    assert "from chispa import assert_df_equality" in test_content
    assert "from my_spark_app.jobs.example import run, transform" in test_content


def test_scaffold_files_spark_notebook_valid_json(tmp_path: Path) -> None:
    import json as json_mod

    target = tmp_path / "my-spark-app"
    target.mkdir()
    scaffold_files(target, name="my-spark-app", module_name="my_spark_app", archetype="spark", python_version="3.13")
    notebook = json_mod.loads((target / "notebooks" / "explore.ipynb").read_text())
    assert notebook["nbformat"] == 4
    assert "SparkSession" in str(notebook["cells"])
    assert notebook["metadata"]["language_info"]["version"] == "3.13.0"


def test_scaffold_files_spark_end_with_trailing_newline(tmp_path: Path) -> None:
    target = tmp_path / "my-spark-app"
    target.mkdir()
    scaffold_files(target, name="my-spark-app", module_name="my_spark_app", archetype="spark", python_version="3.13")

    generated_files = [
        ".python-version",
        ".gitignore",
        "main.py",
        "pyproject.toml",
        "README.md",
        "src/my_spark_app/__init__.py",
        "src/my_spark_app/_logging.py",
        "src/my_spark_app/config.py",
        "src/my_spark_app/session.py",
        "src/my_spark_app/jobs/__init__.py",
        "src/my_spark_app/jobs/example.py",
        "tests/__init__.py",
        "tests/conftest.py",
        "tests/test_example.py",
        "notebooks/explore.ipynb",
        "notebooks/explore_marimo.py",
    ]

    for rel_path in generated_files:
        content = (target / rel_path).read_text()
        assert content.endswith("\n"), f"Expected trailing newline in {rel_path}"


# ---------------------------------------------------------------------------
# spark archetype — integration (run_new → scaffold_files → _scaffold_spark)
# ---------------------------------------------------------------------------


def test_run_new_spark_success(tmp_path: Path) -> None:
    with (
        patch("nuv.commands.new.shutil.which", return_value="/usr/bin/uv"),
        patch("nuv.commands.new.subprocess.run") as mock_run,
    ):
        mock_run.return_value = MagicMock(returncode=0)
        result = run_new("my-spark-app", at=str(tmp_path / "my-spark-app"), cwd=tmp_path, archetype="spark")
    assert result == 0
    assert (tmp_path / "my-spark-app" / "main.py").exists()
    assert (tmp_path / "my-spark-app" / "src" / "my_spark_app" / "config.py").exists()
    assert (tmp_path / "my-spark-app" / "notebooks" / "explore.ipynb").exists()


def test_run_new_spark_cleanup_on_failure(tmp_path: Path) -> None:
    with patch("nuv.commands.new.shutil.which", return_value=None):
        result = run_new("my-spark-app", cwd=tmp_path, archetype="spark")
    assert result == 1
    assert not (tmp_path / "my-spark-app").exists()


def test_run_new_spark_keep_on_failure(tmp_path: Path) -> None:
    with patch("nuv.commands.new.shutil.which", return_value=None):
        result = run_new("my-spark-app", cwd=tmp_path, archetype="spark", keep_on_failure=True)
    assert result == 1
    assert (tmp_path / "my-spark-app").exists()


# ---------------------------------------------------------------------------
# spark archetype — CLI
# ---------------------------------------------------------------------------


def test_cli_new_spark_archetype(tmp_path: Path) -> None:
    with (
        patch("nuv.commands.new.shutil.which", return_value="/usr/bin/uv"),
        patch("nuv.commands.new.subprocess.run") as mock_run,
    ):
        mock_run.return_value = MagicMock(returncode=0)
        result = cli_main(["new", "my-spark-app", "--at", str(tmp_path / "my-spark-app"), "--archetype", "spark"])
    assert result == 0
    assert (tmp_path / "my-spark-app" / "src" / "my_spark_app" / "__init__.py").exists()
    assert (tmp_path / "my-spark-app" / "notebooks" / "explore.ipynb").exists()


def test_cli_spark_default_python_version(tmp_path: Path) -> None:
    with (
        patch("nuv.commands.new.shutil.which", return_value="/usr/bin/uv"),
        patch("nuv.commands.new.subprocess.run") as mock_run,
    ):
        mock_run.return_value = MagicMock(returncode=0)
        result = cli_main(["new", "my-spark-app", "--at", str(tmp_path / "my-spark-app"), "--archetype", "spark"])
    assert result == 0
    assert (tmp_path / "my-spark-app" / ".python-version").read_text().strip() == "3.13"


# ---------------------------------------------------------------------------
# fastapi archetype — scaffold_files
# ---------------------------------------------------------------------------


def test_scaffold_files_fastapi_creates_expected_files(tmp_path: Path) -> None:
    target = tmp_path / "my-api"
    target.mkdir()
    scaffold_files(target, name="my-api", module_name="my_api", archetype="fastapi")

    assert (target / ".python-version").exists()
    assert (target / ".gitignore").exists()
    assert (target / "main.py").exists()
    assert (target / "pyproject.toml").exists()
    assert (target / "README.md").exists()
    assert (target / "Dockerfile").exists()
    assert (target / ".dockerignore").exists()
    assert (target / "src" / "my_api" / "__init__.py").exists()
    assert (target / "src" / "my_api" / "app.py").exists()
    assert (target / "src" / "my_api" / "config.py").exists()
    assert (target / "src" / "my_api" / "_logging.py").exists()
    assert (target / "src" / "my_api" / "dependencies.py").exists()
    assert (target / "src" / "my_api" / "routes" / "__init__.py").exists()
    assert (target / "src" / "my_api" / "routes" / "health.py").exists()
    assert (target / "tests" / "__init__.py").exists()
    assert (target / "tests" / "conftest.py").exists()
    assert (target / "tests" / "test_health.py").exists()


def test_scaffold_files_fastapi_pyproject_has_deps(tmp_path: Path) -> None:
    target = tmp_path / "my-api"
    target.mkdir()
    scaffold_files(target, name="my-api", module_name="my_api", archetype="fastapi")
    pyproject = (target / "pyproject.toml").read_text()
    assert "fastapi>=0.136.1" in pyproject
    assert "granian>=2.7.4" in pyproject
    assert "pydantic-settings>=2.14.0" in pyproject
    assert "httpx>=0.28.1" in pyproject
    assert "pytest-asyncio>=1.3.0" in pyproject
    assert "py314" in pyproject
    assert 'packages = ["src/my_api"]' in pyproject
    assert 'build-backend = "hatchling.build"' in pyproject


def test_scaffold_files_fastapi_main_imports_package(tmp_path: Path) -> None:
    target = tmp_path / "my-api"
    target.mkdir()
    scaffold_files(target, name="my-api", module_name="my_api", archetype="fastapi")
    main_content = (target / "main.py").read_text()
    assert "from my_api._logging import configure" in main_content
    assert "from granian import Granian" in main_content


def test_scaffold_files_fastapi_app_factory(tmp_path: Path) -> None:
    target = tmp_path / "my-api"
    target.mkdir()
    scaffold_files(target, name="my-api", module_name="my_api", archetype="fastapi")
    app_content = (target / "src" / "my_api" / "app.py").read_text()
    assert "def create_app" in app_content
    assert "lifespan" in app_content


def test_scaffold_files_fastapi_dockerfile_multi_stage(tmp_path: Path) -> None:
    target = tmp_path / "my-api"
    target.mkdir()
    scaffold_files(target, name="my-api", module_name="my_api", archetype="fastapi")
    dockerfile = (target / "Dockerfile").read_text()
    assert "AS builder" in dockerfile
    assert "python:3.14-slim-bookworm" in dockerfile  # default python_version
    assert "USER app" in dockerfile
    assert "my_api.app:create_app" in dockerfile


def test_scaffold_files_fastapi_test_uses_httpx(tmp_path: Path) -> None:
    target = tmp_path / "my-api"
    target.mkdir()
    scaffold_files(target, name="my-api", module_name="my_api", archetype="fastapi")
    test_content = (target / "tests" / "test_health.py").read_text()
    assert "from httpx import AsyncClient" in test_content
    assert "from my_api.app import create_app" in test_content


def test_scaffold_files_fastapi_end_with_trailing_newline(tmp_path: Path) -> None:
    target = tmp_path / "my-api"
    target.mkdir()
    scaffold_files(target, name="my-api", module_name="my_api", archetype="fastapi")

    generated_files = [
        ".python-version",
        ".gitignore",
        "main.py",
        "pyproject.toml",
        "README.md",
        "Dockerfile",
        ".dockerignore",
        "src/my_api/__init__.py",
        "src/my_api/app.py",
        "src/my_api/config.py",
        "src/my_api/_logging.py",
        "src/my_api/dependencies.py",
        "src/my_api/routes/__init__.py",
        "src/my_api/routes/health.py",
        "tests/__init__.py",
        "tests/conftest.py",
        "tests/test_health.py",
    ]

    for rel_path in generated_files:
        content = (target / rel_path).read_text()
        assert content.endswith("\n"), f"Expected trailing newline in {rel_path}"


# ---------------------------------------------------------------------------
# fastapi archetype — integration (run_new → scaffold_files → _scaffold_fastapi)
# ---------------------------------------------------------------------------


def test_run_new_fastapi_success(tmp_path: Path) -> None:
    with (
        patch("nuv.commands.new.shutil.which", return_value="/usr/bin/uv"),
        patch("nuv.commands.new.subprocess.run") as mock_run,
    ):
        mock_run.return_value = MagicMock(returncode=0)
        result = run_new("my-api", at=str(tmp_path / "my-api"), cwd=tmp_path, archetype="fastapi")
    assert result == 0
    assert (tmp_path / "my-api" / "main.py").exists()
    assert (tmp_path / "my-api" / "src" / "my_api" / "app.py").exists()
    assert (tmp_path / "my-api" / "Dockerfile").exists()


def test_run_new_fastapi_cleanup_on_failure(tmp_path: Path) -> None:
    with patch("nuv.commands.new.shutil.which", return_value=None):
        result = run_new("my-api", cwd=tmp_path, archetype="fastapi")
    assert result == 1
    assert not (tmp_path / "my-api").exists()


def test_run_new_fastapi_keep_on_failure(tmp_path: Path) -> None:
    with patch("nuv.commands.new.shutil.which", return_value=None):
        result = run_new("my-api", cwd=tmp_path, archetype="fastapi", keep_on_failure=True)
    assert result == 1
    assert (tmp_path / "my-api").exists()


# ---------------------------------------------------------------------------
# fastapi archetype — CLI
# ---------------------------------------------------------------------------


def test_cli_new_fastapi_archetype(tmp_path: Path) -> None:
    with (
        patch("nuv.commands.new.shutil.which", return_value="/usr/bin/uv"),
        patch("nuv.commands.new.subprocess.run") as mock_run,
    ):
        mock_run.return_value = MagicMock(returncode=0)
        result = cli_main(["new", "my-api", "--at", str(tmp_path / "my-api"), "--archetype", "fastapi"])
    assert result == 0
    assert (tmp_path / "my-api" / "src" / "my_api" / "__init__.py").exists()
    assert (tmp_path / "my-api" / "Dockerfile").exists()


def test_cli_fastapi_default_python_version(tmp_path: Path) -> None:
    with (
        patch("nuv.commands.new.shutil.which", return_value="/usr/bin/uv"),
        patch("nuv.commands.new.subprocess.run") as mock_run,
    ):
        mock_run.return_value = MagicMock(returncode=0)
        result = cli_main(["new", "my-api", "--at", str(tmp_path / "my-api"), "--archetype", "fastapi"])
    assert result == 0
    assert (tmp_path / "my-api" / ".python-version").read_text().strip() == "3.14"


def test_default_python_versions_fastapi() -> None:
    assert DEFAULT_PYTHON_VERSIONS["fastapi"] == "3.14"


def test_run_new_fastapi_uses_default_python_314(tmp_path: Path) -> None:
    with (
        patch("nuv.commands.new.shutil.which", return_value="/usr/bin/uv"),
        patch("nuv.commands.new.subprocess.run") as mock_run,
        patch("nuv.commands.new.scaffold_files") as mock_scaffold,
    ):
        mock_run.return_value = MagicMock(returncode=0)
        result = run_new("my-api", at=str(tmp_path / "my-api"), cwd=tmp_path, archetype="fastapi")
    assert result == 0
    mock_scaffold.assert_called_once()
    call_kwargs = mock_scaffold.call_args[1]
    assert call_kwargs["python_version"] == "3.14"
    assert call_kwargs["archetype"] == "fastapi"


# ---------------------------------------------------------------------------
# polars archetype — scaffold_files
# ---------------------------------------------------------------------------


def test_default_python_versions_polars() -> None:
    assert DEFAULT_PYTHON_VERSIONS["polars"] == "3.14"


def test_scaffold_files_polars_creates_expected_files(tmp_path: Path) -> None:
    target = tmp_path / "my-polars-app"
    target.mkdir()
    scaffold_files(target, name="my-polars-app", module_name="my_polars_app", archetype="polars")

    assert (target / ".python-version").exists()
    assert (target / ".gitignore").exists()
    assert (target / "main.py").exists()
    assert (target / "pyproject.toml").exists()
    assert (target / "README.md").exists()
    assert (target / "src" / "my_polars_app" / "__init__.py").exists()
    assert (target / "src" / "my_polars_app" / "_logging.py").exists()
    assert (target / "src" / "my_polars_app" / "_io.py").exists()
    assert (target / "src" / "my_polars_app" / "_db.py").exists()
    assert (target / "src" / "my_polars_app" / "config.py").exists()
    assert (target / "src" / "my_polars_app" / "main.py").exists()
    assert (target / "tests" / "__init__.py").exists()
    assert (target / "tests" / "conftest.py").exists()
    assert (target / "tests" / "test_io.py").exists()
    assert (target / "notebooks" / "explore.py").exists()
    assert (target / "data" / "raw").exists()
    assert (target / "data" / "features").exists()


def test_scaffold_files_polars_pyproject_has_deps(tmp_path: Path) -> None:
    target = tmp_path / "my-polars-app"
    target.mkdir()
    scaffold_files(target, name="my-polars-app", module_name="my_polars_app", archetype="polars")
    pyproject = (target / "pyproject.toml").read_text()
    assert "polars>=1.40.1" in pyproject
    assert "duckdb>=1.5.2" in pyproject
    assert "deltalake>=1.5.1" in pyproject
    assert "pydantic-settings>=2.14.0" in pyproject
    assert "click>=8.3.3" in pyproject
    assert "marimo>=0.23.4" in pyproject
    assert "py314" in pyproject
    assert 'packages = ["src/my_polars_app"]' in pyproject
    assert 'build-backend = "hatchling.build"' in pyproject


def test_scaffold_files_polars_main_uses_click(tmp_path: Path) -> None:
    target = tmp_path / "my-polars-app"
    target.mkdir()
    scaffold_files(target, name="my-polars-app", module_name="my_polars_app", archetype="polars")
    main_content = (target / "main.py").read_text()
    assert "import click" in main_content
    assert "@click.command()" in main_content


def test_scaffold_files_polars_package_modules(tmp_path: Path) -> None:
    target = tmp_path / "my-polars-app"
    target.mkdir()
    scaffold_files(target, name="my-polars-app", module_name="my_polars_app", archetype="polars")
    io_content = (target / "src" / "my_polars_app" / "_io.py").read_text()
    assert "read_csv" in io_content
    assert "read_parquet" in io_content
    assert "show" in io_content
    assert "glimpse" in io_content
    db_content = (target / "src" / "my_polars_app" / "_db.py").read_text()
    assert "import duckdb" in db_content
    assert "def sql" in db_content
    config = (target / "src" / "my_polars_app" / "config.py").read_text()
    assert "pydantic_settings" in config


def test_scaffold_files_polars_end_with_trailing_newline(tmp_path: Path) -> None:
    target = tmp_path / "my-polars-app"
    target.mkdir()
    scaffold_files(target, name="my-polars-app", module_name="my_polars_app", archetype="polars")

    generated_files = [
        ".python-version",
        ".gitignore",
        "main.py",
        "pyproject.toml",
        "README.md",
        "src/my_polars_app/__init__.py",
        "src/my_polars_app/_logging.py",
        "src/my_polars_app/_io.py",
        "src/my_polars_app/_db.py",
        "src/my_polars_app/config.py",
        "src/my_polars_app/main.py",
        "tests/__init__.py",
        "tests/conftest.py",
        "tests/test_io.py",
        "notebooks/explore.py",
    ]

    for rel_path in generated_files:
        content = (target / rel_path).read_text()
        assert content.endswith("\n"), f"Expected trailing newline in {rel_path}"


# ---------------------------------------------------------------------------
# polars archetype — integration (run_new → scaffold_files → _scaffold_polars)
# ---------------------------------------------------------------------------


def test_run_new_polars_success(tmp_path: Path) -> None:
    with (
        patch("nuv.commands.new.shutil.which", return_value="/usr/bin/uv"),
        patch("nuv.commands.new.subprocess.run") as mock_run,
    ):
        mock_run.return_value = MagicMock(returncode=0)
        result = run_new("my-polars-app", at=str(tmp_path / "my-polars-app"), cwd=tmp_path, archetype="polars")
    assert result == 0
    assert (tmp_path / "my-polars-app" / "main.py").exists()
    assert (tmp_path / "my-polars-app" / "src" / "my_polars_app" / "_io.py").exists()
    assert (tmp_path / "my-polars-app" / "notebooks" / "explore.py").exists()
    assert (tmp_path / "my-polars-app" / "data" / "raw").exists()


def test_run_new_polars_cleanup_on_failure(tmp_path: Path) -> None:
    with patch("nuv.commands.new.shutil.which", return_value=None):
        result = run_new("my-polars-app", cwd=tmp_path, archetype="polars")
    assert result == 1
    assert not (tmp_path / "my-polars-app").exists()


def test_run_new_polars_keep_on_failure(tmp_path: Path) -> None:
    with patch("nuv.commands.new.shutil.which", return_value=None):
        result = run_new("my-polars-app", cwd=tmp_path, archetype="polars", keep_on_failure=True)
    assert result == 1
    assert (tmp_path / "my-polars-app").exists()


# ---------------------------------------------------------------------------
# polars archetype — CLI
# ---------------------------------------------------------------------------


def test_cli_new_polars_archetype(tmp_path: Path) -> None:
    with (
        patch("nuv.commands.new.shutil.which", return_value="/usr/bin/uv"),
        patch("nuv.commands.new.subprocess.run") as mock_run,
    ):
        mock_run.return_value = MagicMock(returncode=0)
        result = cli_main(["new", "my-polars-app", "--at", str(tmp_path / "my-polars-app"), "--archetype", "polars"])
    assert result == 0
    assert (tmp_path / "my-polars-app" / "src" / "my_polars_app" / "__init__.py").exists()
    assert (tmp_path / "my-polars-app" / "data" / "raw").exists()


def test_cli_polars_default_python_version(tmp_path: Path) -> None:
    with (
        patch("nuv.commands.new.shutil.which", return_value="/usr/bin/uv"),
        patch("nuv.commands.new.subprocess.run") as mock_run,
    ):
        mock_run.return_value = MagicMock(returncode=0)
        result = cli_main(["new", "my-polars-app", "--at", str(tmp_path / "my-polars-app"), "--archetype", "polars"])
    assert result == 0
    assert (tmp_path / "my-polars-app" / ".python-version").read_text().strip() == "3.14"


def test_run_new_polars_uses_default_python_314(tmp_path: Path) -> None:
    with (
        patch("nuv.commands.new.shutil.which", return_value="/usr/bin/uv"),
        patch("nuv.commands.new.subprocess.run") as mock_run,
        patch("nuv.commands.new.scaffold_files") as mock_scaffold,
    ):
        mock_run.return_value = MagicMock(returncode=0)
        result = run_new("my-polars-app", at=str(tmp_path / "my-polars-app"), cwd=tmp_path, archetype="polars")
    assert result == 0
    mock_scaffold.assert_called_once()
    call_kwargs = mock_scaffold.call_args[1]
    assert call_kwargs["python_version"] == "3.14"
    assert call_kwargs["archetype"] == "polars"
