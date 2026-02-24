import pytest

from nuv.cli import main
from nuv.commands.new import validate_name


def test_no_command_returns_1() -> None:
    assert main([]) == 1


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


from unittest.mock import MagicMock, patch

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
