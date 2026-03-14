"""Entry point for {name}."""

import argparse
from collections.abc import Sequence

from granian import Granian
from granian.constants import Interfaces

from {module_name}._logging import configure


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="{name}")
    parser.add_argument("--host", default="0.0.0.0", help="Bind host (default: 0.0.0.0).")
    parser.add_argument("--port", type=int, default=8000, help="Bind port (default: 8000).")
    parser.add_argument(
        "--log-level",
        default="WARNING",
        choices=("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"),
        help="Logging level (default: WARNING).",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    configure(args.log_level)
    server = Granian(
        "{module_name}.app:create_app",
        interface=Interfaces.ASGI,
        factory=True,
        host=args.host,
        port=args.port,
    )
    server.serve()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
