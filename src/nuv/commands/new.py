import re
from pathlib import Path


def validate_name(name: str) -> str:
    if not name:
        raise ValueError("Name cannot be empty.")
    if " " in name:
        raise ValueError("Name cannot contain spaces.")
    if name.startswith("-"):
        raise ValueError("Name cannot start with a leading hyphen.")
    if not re.fullmatch(r"[a-zA-Z0-9_\-]+", name):
        raise ValueError(f"Name contains invalid characters: {name!r}")
    return name


def resolve_target(name: str, *, at: str | None, cwd: Path) -> Path:
    target = Path(at) if at else cwd / name
    if target.exists():
        raise ValueError(f"Directory already exists: {target}")
    return target


def run_new(name: str, *, at: str | None = None) -> int:
    return 0
