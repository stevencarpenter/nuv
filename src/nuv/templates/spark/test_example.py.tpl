from chispa import assert_df_equality

from {module_name}.jobs.example import transform


def test_transform_filters_low_values(spark):
    source = spark.createDataFrame(
        [("alice", 1), ("bob", 2), ("charlie", 3)],
        ["name", "value"],
    )
    expected = spark.createDataFrame(
        [("bob", 2), ("charlie", 3)],
        ["name", "value"],
    )
    result = transform(source)
    assert_df_equality(result, expected, ignore_row_order=True)
