import polars as pl
import pytest


@pytest.fixture
def sample_df() -> pl.DataFrame:
    return pl.DataFrame({{"x": [1, 2, 3], "y": ["a", "b", "c"]}})