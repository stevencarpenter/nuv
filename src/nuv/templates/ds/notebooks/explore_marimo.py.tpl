import marimo

__generated_with = "0.23.8"
app = marimo.App(width="medium")


@app.cell
def _():
    import numpy as np
    import pandas as pd

    from {module_name}.data import preview, summary

    return np, pd, preview, summary


@app.cell
def _(pd):
    df = pd.DataFrame({{"x": [1, 2, 3], "y": ["a", "b", "c"]}})
    df
    return (df,)


@app.cell
def _(df, summary):
    summary(df)
    return


if __name__ == "__main__":
    app.run()
