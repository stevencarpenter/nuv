import argparse
from collections.abc import Sequence

from nuv._logging import configure
from nuv.commands.new import DEFAULT_PYTHON_VERSION, validate_python_version


def _parse_python_version(value: str) -> str:
    try:
        return validate_python_version(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(str(exc)) from exc


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
    new_parser.add_argument("--at", metavar="PATH", help="Target directory (default: ./<name>).")
    new_parser.add_argument(
        "--archetype",
        default="script",
        choices=["script"],
        metavar="TYPE",
        help="Project archetype (default: script).",
    )
    new_parser.add_argument(
        "--python-version",
        default=DEFAULT_PYTHON_VERSION,
        metavar="VERSION",
        type=_parse_python_version,
        help=f"Python version for the generated project (default: {DEFAULT_PYTHON_VERSION}). Must be MAJOR.MINOR format.",
    )

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    from nuv.commands.new import run_new

    parser = build_parser()
    args = parser.parse_args(argv)
    configure(args.log_level)

    if args.command == "new":
        return run_new(
            args.name,
            at=args.at,
            archetype=args.archetype,
            python_version=args.python_version,
        )

    parser.print_help()
    return 1
