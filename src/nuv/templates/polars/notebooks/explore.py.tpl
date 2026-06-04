import marimo

__generated_with = "0.23.8"
app = marimo.App(width="medium")


@app.cell
def _():
    import polars as pl

    from {module_name}._db import sql
    from {module_name}._io import glimpse, read_csv, read_parquet, show

    pl
    return (pl, read_csv, read_parquet, show, glimpse, sql)


@app.cell
def _(pl):
    df = pl.DataFrame({{"x": [1, 2, 3], "y": ["a", "b", "c"]}})
    df
    return (df,)


if __name__ == "__main__":
    app.run()
