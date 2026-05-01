import marimo

__generated_with = "0.23.4"
app = marimo.App(width="medium")


@app.cell
def _():
    from pyspark.sql import SparkSession

    spark = SparkSession.builder.master("local[*]").appName("{name}").getOrCreate()
    spark
    return (spark,)


@app.cell
def _(spark):
    data = [("alice", 1), ("bob", 2), ("charlie", 3)]
    df = spark.createDataFrame(data, ["name", "value"])
    df.show()
    return (df,)


@app.cell
def _(df):
    filtered = df.filter(df.value > 1)
    filtered.show()
    return (filtered,)


@app.cell
def _(df):
    grouped = df.groupBy("name").sum("value")
    grouped.show()
    return (grouped,)


if __name__ == "__main__":
    app.run()
