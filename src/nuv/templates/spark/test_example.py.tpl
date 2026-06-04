import logging
import sys
from unittest.mock import MagicMock, patch

import pytest
from chispa import assert_df_equality

from {module_name}._logging import configure
from {module_name}.config import resolve_params
from {module_name}.jobs.example import run, transform
from {module_name}.main import main
from {module_name}.session import create_spark_session

# --- Main ---


def test_main_returns_zero():
    mock_spark = MagicMock()
    with (
        patch("{module_name}.main.create_spark_session", return_value=mock_spark),
        patch("{module_name}.main.example"),
    ):
        result = main([])
    assert result == 0
    mock_spark.stop.assert_called_once()


def test_main_returns_2_for_usage_errors(capsys):
    result = main(["--bogus"])
    assert result == 2
    assert "No such option" in capsys.readouterr().err


def test_main_returns_0_for_help(capsys):
    result = main(["--help"])
    assert result == 0
    assert "--env" in capsys.readouterr().out


def test_main_preserves_job_error_when_stop_also_fails():
    mock_spark = MagicMock()
    mock_spark.stop.side_effect = RuntimeError("stop failed")
    with (
        patch("{module_name}.main.create_spark_session", return_value=mock_spark),
        patch("{module_name}.main.example.run", side_effect=ValueError("job failed")),
        pytest.raises(ValueError, match="job failed"),
    ):
        main([])


def test_main_raises_stop_error_when_job_succeeds():
    mock_spark = MagicMock()
    mock_spark.stop.side_effect = RuntimeError("stop failed")
    with (
        patch("{module_name}.main.create_spark_session", return_value=mock_spark),
        patch("{module_name}.main.example.run"),
        pytest.raises(RuntimeError, match="stop failed"),
    ):
        main([])


# --- Jobs ---


def test_transform_filters_low_values(spark):
    source = spark.createDataFrame(
        [("alice", 1), ("bob", 2), ("charlie", 3)],
        ["name", "value"],
    )
    expected = spark.createDataFrame(
        [("bob", 2), ("charlie", 3)],
        ["name", "value"],
    )
    result = transform(source)
    assert_df_equality(result, expected, ignore_row_order=True)


def test_run_returns_filtered_dataframe(spark):
    result = run(spark, {{"env": "dev", "job": "example", "log_level": "WARNING"}})
    assert result.count() == 2


# --- Config ---


def test_resolve_params_defaults():
    params = resolve_params([])
    assert params["env"] == "dev"
    assert params["job"] == "example"
    assert params["log_level"] == "WARNING"


def test_resolve_params_cli_overrides():
    params = resolve_params(["--env", "prod", "--job", "etl"])
    assert params["env"] == "prod"
    assert params["job"] == "etl"


def test_resolve_params_env_var(monkeypatch):
    monkeypatch.setenv("SPARK_APP_ENV", "staging")
    params = resolve_params([])
    assert params["env"] == "staging"


def test_resolve_params_reads_sys_argv(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["main.py", "--env", "prod", "--job", "etl", "--log-level", "INFO"])
    params = resolve_params(None)
    assert params == {{"env": "prod", "job": "etl", "log_level": "INFO"}}


# --- Logging ---


def test_configure_suppresses_spark_loggers():
    configure("WARNING")
    assert logging.getLogger("py4j").level == logging.WARNING
    assert logging.getLogger("pyspark").level == logging.WARNING


# --- Session ---


def test_create_spark_session_returns_active_session(spark):
    session = create_spark_session("test-app")
    assert session is not None
