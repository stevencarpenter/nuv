import pandas as pd
import pytest


@pytest.fixture
def sample_df() -> pd.DataFrame:
    return pd.DataFrame({{"x": [1, 2, 3], "y": ["a", "b", "c"]}})
