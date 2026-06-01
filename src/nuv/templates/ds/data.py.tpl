"""Tabular I/O helpers built on pandas.

Read/write CSV, Parquet, and JSON, plus a couple of quick-look helpers for
the REPL and notebooks. Swap pandas for polars (uncomment it in
pyproject.toml) once a dataset outgrows comfortable in-memory pandas.

Note: JSON does not preserve dtypes (datetimes round-trip as strings, not
``datetime64``). Reach for Parquet when you need full-fidelity round-trips.
"""

from pathlib import Path

import pandas as pd


def read_csv(path: str | Path, **kwargs) -> pd.DataFrame:
    return pd.read_csv(path, **kwargs)


def read_parquet(path: str | Path, **kwargs) -> pd.DataFrame:
    return pd.read_parquet(path, **kwargs)


def read_json(path: str | Path, **kwargs) -> pd.DataFrame:
    return pd.read_json(path, **kwargs)


def write(df: pd.DataFrame, path: str | Path, **kwargs) -> None:
    path = Path(path)
    suffix = path.suffix.lower()
    if suffix == ".csv":
        df.to_csv(path, index=False, **kwargs)
    elif suffix == ".parquet":
        df.to_parquet(path, **kwargs)
    elif suffix == ".json":
        kwargs.setdefault("date_format", "iso")
        df.to_json(path, **kwargs)
    else:
        raise ValueError(f"Unsupported format: {{suffix}}")


def preview(df: pd.DataFrame, n: int = 10) -> None:
    print(df.head(n))


def summary(df: pd.DataFrame) -> None:
    n_rows, n_cols = df.shape
    print(f"Rows: {{n_rows:,}}    Columns: {{n_cols:,}}")
    print(df.dtypes)
