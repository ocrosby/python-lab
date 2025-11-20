"""Application settings."""

from dataclasses import dataclass


@dataclass
class Settings:
    """Application settings."""

    app_name: str = "FastAPI Basic Example"
    app_version: str = "1.0.0"
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = True


settings = Settings()
