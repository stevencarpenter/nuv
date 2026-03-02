"""Resolve parameters from CLI args, environment variables, and defaults."""

import argparse
import os
from collections.abc import Sequence

DEFAULTS: dict[str, str] = {{
    "env": "dev",
    "job": "example",
    "log_level": "WARNING",
}}


def resolve_params(argv: Sequence[str] | None = None) -> dict[str, str]:
    parser = argparse.ArgumentParser(description="{name}")
    parser.add_argument("--env", default=None, help="Environment (default: dev).")
    parser.add_argument("--job", default=None, help="Job to run (default: example).")
    parser.add_argument(
        "--log-level",
        dest="log_level",
        default=None,
        choices=("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"),
        help="Logging level (default: WARNING).",
    )
    parsed = parser.parse_args(argv)

    params: dict[str, str] = {{}}
    for key, default in DEFAULTS.items():
        cli_val = getattr(parsed, key, None)
        env_val = os.environ.get(f"SPARK_APP_{{key.upper()}}")
        params[key] = cli_val or env_val or default
    return params
