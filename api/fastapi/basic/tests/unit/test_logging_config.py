"""Unit tests for logging configuration."""

import pytest

from src.fastapi_basic_example.infrastructure.logging.config import configure_logging


@pytest.mark.unit
class TestLoggingConfig:
    """Test cases for logging configuration."""

    def test_configure_logging_with_json(self):
        """Test configuring logging with JSON output."""
        configure_logging(log_level="INFO", use_json=True)

    def test_configure_logging_without_json(self):
        """Test configuring logging without JSON output."""
        configure_logging(log_level="DEBUG", use_json=False)
