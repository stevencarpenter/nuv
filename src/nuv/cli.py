import argparse
from collections.abc import Sequence


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="nuv",
        description="Scaffold opinionated uv Python projects.",
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
        metavar="TYPE",
        help="Project archetype (default: script).",
    )

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    from nuv.commands.new import run_new

    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "new":
        return run_new(args.name, at=args.at, archetype=args.archetype)

    parser.print_help()
    return 1
