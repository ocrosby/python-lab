"""Unit tests for logging configuration."""

import pytest

from src.fastapi_basic_example.infrastructure.logging.config import (
    configure_logging,
    get_logger,
    get_uvicorn_log_config,
)


@pytest.mark.unit
class TestLoggingConfig:
    """Test cases for logging configuration."""

    def test_configure_logging_with_json(self):
        """Test configuring logging with JSON output."""
        configure_logging(log_level="INFO", use_json=True)

    def test_configure_logging_without_json(self):
        """Test configuring logging without JSON output."""
        configure_logging(log_level="DEBUG", use_json=False)

    def test_get_logger(self):
        """Test getting a logger instance."""
        logger = get_logger("test_logger")
        assert logger is not None

    def test_get_uvicorn_log_config_with_json(self):
        """Test getting uvicorn config with JSON formatter."""
        config = get_uvicorn_log_config(log_level="debug", use_json=True)

        assert config is not None
        assert "version" in config
        assert "formatters" in config
        assert "default" in config["formatters"]

    def test_get_uvicorn_log_config_without_json(self):
        """Test getting uvicorn config without JSON formatter."""
        config = get_uvicorn_log_config(log_level="info", use_json=False)

        assert config is not None
        assert "version" in config
        assert "formatters" in config
        assert "default" in config["formatters"]
        assert "format" in config["formatters"]["default"]
