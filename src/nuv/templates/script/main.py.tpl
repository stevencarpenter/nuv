import logging
from collections.abc import Sequence

import click

from _logging import configure

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

PROJECT_NAME = "{name}"

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


@click.command()
@click.option(
    "--log-level",
    default="WARNING",
    show_default=True,
    type=click.Choice(("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")),
    help="Logging level.",
)
def _cli(log_level: str) -> None:
    configure(log_level)
    log.debug("Starting %s", PROJECT_NAME)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main(argv: Sequence[str] | None = None) -> int:
    try:
        _cli.main(args=list(argv) if argv is not None else None, standalone_mode=False)
    except click.exceptions.UsageError as exc:
        exc.show()
        return exc.exit_code
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
