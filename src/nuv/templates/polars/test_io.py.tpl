import polars as pl
from polars.testing import assert_frame_equal

from {module_name}._io import (
    glimpse,
    read_csv,
    read_delta,
    read_json,
    read_parquet,
    show,
    write,
    write_delta,
)


def test_read_parquet_roundtrip(tmp_path):
    df = pl.DataFrame({{"x": [1, 2, 3], "y": ["a", "b", "c"]}})
    path = tmp_path / "test.parquet"
    write(df, path)
    result = read_parquet(path)
    assert_frame_equal(result, df)


def test_read_csv_roundtrip(tmp_path):
    df = pl.DataFrame({{"x": [1, 2, 3], "y": ["a", "b", "c"]}})
    path = tmp_path / "test.csv"
    write(df, path)
    result = read_csv(path)
    assert_frame_equal(result, df)


def test_read_json_roundtrip(tmp_path):
    df = pl.DataFrame({{"x": [1, 2, 3], "y": ["a", "b", "c"]}})
    path = tmp_path / "test.json"
    write(df, path)
    result = read_json(path)
    assert_frame_equal(result, df)


def test_write_unsupported_format(sample_df, tmp_path):
    import pytest

    path = tmp_path / "test.xyz"
    with pytest.raises(ValueError, match="Unsupported format"):
        write(sample_df, path)


def test_read_delta_roundtrip(tmp_path):
    df = pl.DataFrame({{"x": [1, 2, 3], "y": ["a", "b", "c"]}})
    path = tmp_path / "delta-table"
    write_delta(df, path)
    result = read_delta(path)
    assert_frame_equal(result, df)


def test_show_does_not_raise(sample_df):
    show(sample_df)


def test_glimpse_does_not_raise(sample_df):
    glimpse(sample_df)