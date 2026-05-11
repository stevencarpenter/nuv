"""Resolve parameters from CLI args, environment variables, and defaults."""

from collections.abc import Sequence

import click


def resolve_params(argv: Sequence[str] | None = None) -> dict[str, str]:
    captured: dict[str, str] = {{}}

    @click.command()
    @click.option("--env", envvar="SPARK_APP_ENV", default="dev", show_default=True, help="Environment.")
    @click.option("--job", envvar="SPARK_APP_JOB", default="example", show_default=True, help="Job to run.")
    @click.option(
        "--log-level",
        "log_level",
        envvar="SPARK_APP_LOG_LEVEL",
        default="WARNING",
        show_default=True,
        type=click.Choice(("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")),
        help="Logging level.",
    )
    def _cli(env: str, job: str, log_level: str) -> None:
        captured["env"] = env
        captured["job"] = job
        captured["log_level"] = log_level

    exit_code = _cli.main(args=list(argv) if argv is not None else None, standalone_mode=False)
    if not captured:
        raise click.exceptions.Exit(exit_code if isinstance(exit_code, int) else 0)
    return captured
