"""Application settings."""

from pydantic import BaseModel

from ...domain.constants import AppConstants, ServerConstants


class Settings(BaseModel):
    """Application settings."""

    app_name: str = AppConstants.NAME
    app_version: str = AppConstants.VERSION
    host: str = ServerConstants.DEFAULT_HOST
    port: int = ServerConstants.DEFAULT_PORT
    reload: bool = True


settings = Settings()
