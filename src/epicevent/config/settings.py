import os
from functools import lru_cache
from pathlib import Path

from pydantic import ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict

from epicevent.exception import ConfigurationError

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_TOKEN_PATH = PROJECT_ROOT / ".epicevent" / "tokens.json"


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    # Database
    ###############
    database_url: str

    # Security
    ###############
    secret_key: str

    # Monitoring
    ###############
    sentry_dsn: str | None = None

    # JWT
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 10
    algorithm: str = "HS256"

    # Storage
    ###############
    token_path: Path = DEFAULT_TOKEN_PATH

    model_config = SettingsConfigDict(
        env_file=os.getenv("ENV_FILE", ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """Load and cache application settings.

    Raises:
        ConfigurationError: If the application configuration is invalid.
    """
    try:
        return Settings()
    except ValidationError as exc:
        raise ConfigurationError(exc.errors()) from exc
