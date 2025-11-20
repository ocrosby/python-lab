"""Application settings."""

from pydantic import BaseModel

# Constants to eliminate duplication
APP_NAME = "FastAPI Basic Example"
APP_VERSION = "1.0.0"
DEFAULT_HOST = "0.0.0.0"
DEFAULT_PORT = 8000


class Settings(BaseModel):
    """Application settings."""

    app_name: str = APP_NAME
    app_version: str = APP_VERSION
    host: str = DEFAULT_HOST
    port: int = DEFAULT_PORT
    reload: bool = True


settings = Settings()
