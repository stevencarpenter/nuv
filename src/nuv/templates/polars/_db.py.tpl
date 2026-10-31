import duckdb
import polars as pl


def sql(query: str) -> pl.DataFrame:
    relation = duckdb.sql(query)
    if relation is None:
        raise ValueError(f"Query contains no SQL statement: {{query!r}}")
    return relation.pl()
