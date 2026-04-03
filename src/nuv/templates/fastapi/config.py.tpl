"""Application settings loaded from environment variables."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "{name}"
    debug: bool = False
    log_level: str = "WARNING"
