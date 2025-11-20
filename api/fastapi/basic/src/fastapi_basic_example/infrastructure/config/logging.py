"""Logging configuration settings."""

import os
from typing import Any

from ..logging.config import get_uvicorn_log_config


def get_logging_config() -> dict[str, Any]:
    """Get logging configuration based on environment variables."""
    log_level = os.getenv("LOG_LEVEL", "info").lower()
    use_json = os.getenv("JSON_LOGGING", "false").lower() == "true"

    return get_uvicorn_log_config(log_level=log_level, use_json=use_json)


def should_use_json_logging() -> bool:
    """Check if JSON logging should be used."""
    return os.getenv("JSON_LOGGING", "false").lower() == "true"


def get_log_level() -> str:
    """Get the log level from environment."""
    return os.getenv("LOG_LEVEL", "INFO").upper()
