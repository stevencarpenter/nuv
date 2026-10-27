"""{name}: one line on what this does (shown by --help)."""

import logging
from collections.abc import Sequence

import click

from {module_name}._logging import configure

log = logging.getLogger(__name__)


def run(*, dry_run: bool = False) -> int:
    """Do the work and return a process exit code.

    Keep the logic here, free of CLI concerns, so it can be imported and tested directly.
    Gate every side effect on ``dry_run`` so a rehearsal never changes anything.
    """
    log.info("{name}: nothing to do yet%s", " (dry run)" if dry_run else "")
    return 0


@click.command(help=__doc__)
@click.option("-n", "--dry-run", is_flag=True, help="Report what would change without changing anything.")
@click.option(
    "--log-level",
    default="INFO",
    show_default=True,
    type=click.Choice(("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")),
    help="Logging level.",
)
def _cli(dry_run: bool, log_level: str) -> int:
    configure(log_level)
    return run(dry_run=dry_run)


def main(argv: Sequence[str] | None = None) -> int:
    try:
        result = _cli.main(args=list(argv) if argv is not None else None, prog_name="{name}", standalone_mode=False)
    except click.exceptions.ClickException as exc:
        exc.show()
        return exc.exit_code
    return result if isinstance(result, int) else 0
