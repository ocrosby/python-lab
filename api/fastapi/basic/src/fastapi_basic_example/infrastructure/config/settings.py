"""Application settings."""

from pydantic import field_validator
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
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:8080"]
    cors_allow_credentials: bool = True
    cors_allow_methods: list[str] = ["*"]
    cors_allow_headers: list[str] = ["*"]
    allowed_hosts: list[str] = ["localhost", "127.0.0.1", "*.example.com"]
    gzip_minimum_size: int = 1000
    gzip_compression_level: int = 5

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        upper_v = v.upper()
        if upper_v not in valid_levels:
            raise ValueError(f"log_level must be one of {valid_levels}")
        return upper_v

    @field_validator("port")
    @classmethod
    def validate_port(cls, v: int) -> int:
        if not 1 <= v <= 65535:
            raise ValueError("port must be between 1 and 65535")
        return v


settings = Settings()
