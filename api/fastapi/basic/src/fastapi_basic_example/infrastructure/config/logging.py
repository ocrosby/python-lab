"""Logging configuration settings."""

from typing import Any

from ..logging.config import get_uvicorn_log_config
from .settings import settings


def get_logging_config() -> dict[str, Any]:
    """Get logging configuration based on environment variables."""
    return get_uvicorn_log_config(
        log_level=settings.log_level.lower(), use_json=settings.json_logging
    )


def should_use_json_logging() -> bool:
    """Check if JSON logging should be used."""
    return settings.json_logging


def get_log_level() -> str:
    """Get the log level from environment."""
    return settings.log_level.upper()
