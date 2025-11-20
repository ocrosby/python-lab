"""Application settings."""

from pydantic_settings import BaseSettings, SettingsConfigDict

from ...domain.constants import AppConstants, ServerConstants


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = AppConstants.NAME
    app_version: str = AppConstants.VERSION
    host: str = ServerConstants.DEFAULT_HOST
    port: int = ServerConstants.DEFAULT_PORT
    reload: bool = True
    log_level: str = "INFO"
    json_logging: bool = False


settings = Settings()
