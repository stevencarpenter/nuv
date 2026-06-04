from collections.abc import Sequence

import click

from nuv._logging import configure
from nuv.commands.new import validate_python_version

LOG_LEVELS = ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")
ARCHETYPES = ("script", "spark", "fastapi", "polars", "ds")
INSTALL_MODES = ("editable", "none", "command-only")


def _validate_python_version(ctx: click.Context, param: click.Parameter, value: str | None) -> str | None:
    if value is None:
        return None
    try:
        return validate_python_version(value)
    except ValueError as exc:
        raise click.BadParameter(str(exc), ctx=ctx, param=param) from exc


@click.group(
    name="nuv",
    help="Scaffold opinionated uv Python projects.",
    invoke_without_command=True,
    context_settings={"help_option_names": ["-h", "--help"]},
)
@click.option(
    "--log-level",
    default="WARNING",
    show_default=True,
    type=click.Choice(LOG_LEVELS),
    help="Logging level.",
)
@click.pass_context
def cli(ctx: click.Context, log_level: str) -> None:
    configure(log_level)
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())
        ctx.exit(1)


@cli.command(name="new", help="Create a new project.")
@click.argument("name")
@click.option("--at", "at", metavar="PATH", default=None, help="Target directory (default: ./<name>).")
@click.option(
    "--archetype",
    default="script",
    show_default=True,
    type=click.Choice(ARCHETYPES),
    help="Project archetype.",
)
@click.option(
    "--python-version",
    "python_version",
    default=None,
    metavar="VERSION",
    callback=_validate_python_version,
    help="Python version (default depends on archetype — script=3.14, spark=3.13, fastapi=3.14, polars=3.13, ds=3.13). Must be MAJOR.MINOR format.",
)
@click.option(
    "--install",
    "install_mode",
    default="command-only",
    show_default=True,
    type=click.Choice(INSTALL_MODES),
    help=(
        "Install behavior for the generated project. "
        "editable: run `uv tool install --editable`; "
        "none: skip tool installation; "
        "command-only: log the install command without running it."
    ),
)
@click.option(
    "--keep-on-failure",
    "keep_on_failure",
    is_flag=True,
    default=False,
    help="Keep partially generated files if setup steps fail.",
)
@click.pass_context
def new_cmd(
    ctx: click.Context,
    name: str,
    at: str | None,
    archetype: str,
    python_version: str | None,
    install_mode: str,
    keep_on_failure: bool,
) -> None:
    from nuv.commands.new import run_new

    try:
        exit_code = run_new(
            name,
            at=at,
            archetype=archetype,
            python_version=python_version,
            install_mode=install_mode,
            keep_on_failure=keep_on_failure,
        )
    except Exception as exc:
        click.echo("ERROR unexpected failure", err=True)
        raise SystemExit(1) from exc
    ctx.exit(exit_code)


def main(argv: Sequence[str] | None = None) -> int:
    try:
        result = cli.main(
            args=list(argv) if argv is not None else None,
            standalone_mode=False,
        )
    except click.exceptions.UsageError as exc:
        exc.show()
        raise SystemExit(exc.exit_code) from exc
    return result if isinstance(result, int) else 0
