import duckdb
import polars as pl


def sql(query: str) -> pl.DataFrame:
    return duckdb.sql(query).pl()