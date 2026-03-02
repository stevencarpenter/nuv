"""Example Spark job."""

from pyspark.sql import DataFrame, SparkSession


def run(spark: SparkSession, params: dict[str, str]) -> DataFrame:
    data = [("alice", 1), ("bob", 2), ("charlie", 3)]
    df = spark.createDataFrame(data, ["name", "value"])
    return transform(df)


def transform(df: DataFrame) -> DataFrame:
    return df.filter(df.value > 1)
