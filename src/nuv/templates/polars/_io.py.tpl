from pathlib import Path

import polars as pl


def read_csv(path: str | Path, **kwargs) -> pl.DataFrame:
    return pl.read_csv(path, **kwargs)


def read_parquet(path: str | Path, **kwargs) -> pl.DataFrame:
    return pl.read_parquet(path, **kwargs)


def read_delta(path: str | Path, **kwargs) -> pl.DataFrame:
    return pl.read_delta(path, **kwargs)


def read_json(path: str | Path, **kwargs) -> pl.DataFrame:
    return pl.read_json(path, **kwargs)


def write(df: pl.DataFrame, path: str | Path, **kwargs) -> None:
    path = Path(path)
    suffix = path.suffix.lower()
    if suffix == ".csv":
        df.write_csv(path, **kwargs)
    elif suffix == ".parquet":
        df.write_parquet(path, **kwargs)
    elif suffix == ".json":
        df.write_json(path, **kwargs)
    else:
        raise ValueError(f"Unsupported format: {{suffix}}")


def write_delta(df: pl.DataFrame, path: str | Path, mode: str = "overwrite", **kwargs) -> None:
    df.write_delta(path, mode=mode, **kwargs)


def show(df: pl.DataFrame, max_rows: int = 20) -> None:
    print(df.head(max_rows))


def glimpse(df: pl.DataFrame) -> None:
    n_rows = df.height
    n_cols = df.width
    print(f"Rows: {{n_rows:,}}    Columns: {{n_cols:,}}")
    print(dict(df.schema))