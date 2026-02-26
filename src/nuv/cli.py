import argparse
import logging
import sys
from collections.abc import Sequence

from nuv.commands.new import _PYTHON_VERSION


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="nuv",
        description="Scaffold opinionated uv Python projects.",
    )
    parser.add_argument(
        "--log-level",
        default="WARNING",
        choices=("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"),
        help="Logging level (default: WARNING).",
    )
    subparsers = parser.add_subparsers(dest="command", metavar="<command>")

    new_parser = subparsers.add_parser("new", help="Create a new project.")
    new_parser.add_argument("name", help="Project name.")
    new_parser.add_argument(
        "--at", metavar="PATH", help="Target directory (default: ./<name>)."
    )
    new_parser.add_argument(
        "--archetype",
        default="script",
        choices=["script"],
        metavar="TYPE",
        help="Project archetype (default: script).",
    )
    new_parser.add_argument(
        "--python-version",
        default=_PYTHON_VERSION,
        metavar="VERSION",
        help=f"Python version for the generated project (default: {_PYTHON_VERSION}).",
    )

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    from nuv.commands.new import run_new

    parser = build_parser()
    args = parser.parse_args(argv)
    logging.basicConfig(
        level=args.log_level,
        format="%(levelname)s %(name)s: %(message)s",
        stream=sys.stderr,
    )

    if args.command == "new":
        return run_new(
            args.name,
            at=args.at,
            archetype=args.archetype,
            python_version=args.python_version,
        )

    parser.print_help()
    return 1
