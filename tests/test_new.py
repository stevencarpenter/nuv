from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from nuv.cli import main as cli_main
from nuv.commands.new import (
    DEFAULT_PYTHON_VERSION,
    build_tool_install_command,
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
    assert mock_run.call_count == 2


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


def test_run_new_missing_template(tmp_path: Path) -> None:
    with patch(
        "nuv.commands.new.scaffold_files",
        side_effect=FileNotFoundError("template not found"),
    ):
        result = run_new("my-project", cwd=tmp_path)
    assert result == 1


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
    assert mock_run.call_count == 2


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
