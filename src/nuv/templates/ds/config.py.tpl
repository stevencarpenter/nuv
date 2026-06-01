from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Namespace env vars (e.g. {module_name}_random_seed) so ambient names
    # like RANDOM_SEED / APP_NAME / LOG_LEVEL don't clobber these defaults.
    model_config = SettingsConfigDict(env_prefix="{module_name}_")

    app_name: str = "{name}"
    log_level: str = "INFO"
    data_root: Path = Path("data")
    raw_dir: Path = Path("data/raw")
    processed_dir: Path = Path("data/processed")
    models_dir: Path = Path("models")
    random_seed: int = 42
