"""Entry point for {name}."""

from collections.abc import Sequence

import click

from {module_name}._logging import configure
from {module_name}.config import resolve_params
from {module_name}.jobs import example
from {module_name}.session import create_spark_session


def main(argv: Sequence[str] | None = None) -> int:
    try:
        params = resolve_params(argv)
    except click.exceptions.Exit as exc:
        return exc.exit_code
    except click.exceptions.UsageError as exc:
        exc.show()
        return exc.exit_code
    configure(params["log_level"])
    spark = create_spark_session("{name}")
    try:
        example.run(spark, params)
    finally:
        spark.stop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
