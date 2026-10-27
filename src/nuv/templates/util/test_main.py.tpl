import logging

import pytest

from {module_name}.main import main


def test_main_returns_zero() -> None:
    assert main([]) == 0


def test_main_dry_run_is_logged(caplog: pytest.LogCaptureFixture) -> None:
    with caplog.at_level(logging.INFO):
        assert main(["--dry-run"]) == 0
    assert "dry run" in caplog.text


def test_main_rejects_unknown_option() -> None:
    assert main(["--bogus"]) == 2
