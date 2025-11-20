"""Unit tests for application settings."""

import os
from unittest.mock import patch

import pytest

from src.fastapi_basic_example.infrastructure.config.settings import Settings


@pytest.mark.unit
class TestSettings:
    """Test cases for Settings."""

    def test_settings_defaults(self):
        """Test default settings values."""
        settings = Settings()

        assert settings.app_name == "FastAPI Basic Example"
        assert settings.app_version == "1.0.0"
        assert settings.environment == "development"
        assert settings.debug is True

    @patch.dict(
        os.environ,
        {
            "APP_NAME": "Test App",
            "APP_VERSION": "2.0.0",
            "ENVIRONMENT": "production",
            "DEBUG": "false",
        },
    )
    def test_settings_from_environment(self):
        """Test settings loaded from environment variables."""
        settings = Settings()

        assert settings.app_name == "Test App"
        assert settings.app_version == "2.0.0"
        assert settings.environment == "production"
        assert settings.debug is False

    @patch.dict(os.environ, {"DEBUG": "true"})
    def test_debug_true_from_env(self):
        """Test debug setting as true from environment."""
        settings = Settings()
        assert settings.debug is True

    @patch.dict(os.environ, {"DEBUG": "FALSE"})
    def test_debug_false_case_insensitive(self):
        """Test debug setting is case insensitive."""
        settings = Settings()
        assert settings.debug is False

    @patch.dict(os.environ, {"ENVIRONMENT": "staging"})
    def test_environment_staging(self):
        """Test staging environment setting."""
        settings = Settings()
        assert settings.environment == "staging"

    def test_settings_validation(self):
        """Test settings validation."""
        # This should not raise any exceptions for valid settings
        settings = Settings()
        assert isinstance(settings.app_name, str)
        assert isinstance(settings.app_version, str)
        assert isinstance(settings.environment, str)
        assert isinstance(settings.debug, bool)
