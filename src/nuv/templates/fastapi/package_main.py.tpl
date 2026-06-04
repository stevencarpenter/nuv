"""Entry point for {name}."""

from collections.abc import Sequence

import click
from granian import Granian
from granian.constants import Interfaces

from {module_name}._logging import configure


@click.command()
@click.option("--host", default="0.0.0.0", show_default=True, help="Bind host. 0.0.0.0 exposes all interfaces.")
@click.option("--port", type=int, default=8000, show_default=True, help="Bind port.")
@click.option(
    "--log-level",
    default="WARNING",
    show_default=True,
    type=click.Choice(("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")),
    help="Logging level.",
)
def _cli(host: str, port: int, log_level: str) -> None:
    configure(log_level)
    server = Granian(
        "{module_name}.app:create_app",
        interface=Interfaces.ASGI,
        factory=True,
        address=host,
        port=port,
    )
    server.serve()


def main(argv: Sequence[str] | None = None) -> int:
    try:
        _cli.main(args=list(argv) if argv is not None else None, standalone_mode=False)
    except click.exceptions.UsageError as exc:
        exc.show()
        return exc.exit_code
    return 0
