import argparse
import logging
import sys
from collections.abc import Sequence

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


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="TODO")
    parser.add_argument(
        "--log-level",
        default="WARNING",
        choices=("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"),
        help="Logging level (default: WARNING).",
    )
    return parser


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    return build_parser().parse_args(argv)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    logging.basicConfig(
        level=args.log_level,
        format="%(levelname)s %(name)s: %(message)s",
        stream=sys.stderr,
    )
    log.debug("Starting %s", PROJECT_NAME)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
