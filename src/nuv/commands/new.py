import re
from pathlib import Path
from string import Template


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


_TEMPLATES_DIR = Path(__file__).parent.parent / "templates"


def render_template(tpl_name: str, *, name: str, module_name: str) -> str:
    tpl_path = _TEMPLATES_DIR / tpl_name
    if not tpl_path.exists():
        raise FileNotFoundError(f"Template not found: {tpl_name}")
    return Template(tpl_path.read_text(encoding="utf-8")).substitute(
        name=name,
        module_name=module_name,
    )


def resolve_target(name: str, *, at: str | None, cwd: Path) -> Path:
    target = Path(at) if at else cwd / name
    if target.exists():
        raise ValueError(f"Directory already exists: {target}")
    return target


def run_new(name: str, *, at: str | None = None) -> int:
    return 0
