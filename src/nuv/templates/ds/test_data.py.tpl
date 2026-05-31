import pandas as pd
import pytest
from click.testing import CliRunner
from pandas.testing import assert_frame_equal

from {module_name}._logging import configure
from {module_name}.config import Settings
from {module_name}.data import (
    preview,
    read_csv,
    read_json,
    read_parquet,
    summary,
    write,
)
from {module_name}.main import main


def test_read_parquet_roundtrip(tmp_path):
    df = pd.DataFrame({{"x": [1, 2, 3], "y": ["a", "b", "c"]}})
    path = tmp_path / "test.parquet"
    write(df, path)
    assert_frame_equal(read_parquet(path), df)


def test_read_csv_roundtrip(tmp_path):
    df = pd.DataFrame({{"x": [1, 2, 3], "y": ["a", "b", "c"]}})
    path = tmp_path / "test.csv"
    write(df, path)
    assert_frame_equal(read_csv(path), df)


def test_read_json_roundtrip(tmp_path):
    df = pd.DataFrame({{"x": [1, 2, 3], "y": ["a", "b", "c"]}})
    path = tmp_path / "test.json"
    write(df, path)
    assert_frame_equal(read_json(path), df)


def test_write_unsupported_format(sample_df, tmp_path):
    path = tmp_path / "test.xyz"
    with pytest.raises(ValueError, match="Unsupported format"):
        write(sample_df, path)


def test_preview_does_not_raise(sample_df):
    preview(sample_df)


def test_summary_does_not_raise(sample_df):
    summary(sample_df)


def test_settings_defaults():
    settings = Settings()
    assert settings.app_name == "{name}"
    assert settings.random_seed == 42


def test_configure_does_not_raise():
    configure("INFO")


def test_main_cli_runs():
    result = CliRunner().invoke(main, ["--log-level", "INFO"])
    assert result.exit_code == 0
