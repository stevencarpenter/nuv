from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "{name}"
    log_level: str = "INFO"
    data_root: Path = Path("data")