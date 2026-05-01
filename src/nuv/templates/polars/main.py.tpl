import logging

import click

log = logging.getLogger(__name__)


@click.command()
@click.option(
    "--log-level",
    default="WARNING",
    show_default=True,
    help="Logging level.",
)
def main(log_level: str) -> None:
    from {module_name}._logging import configure
    configure(log_level)
    log.info("Starting {name}")


if __name__ == "__main__":
    main()