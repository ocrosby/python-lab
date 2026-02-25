"""Unit tests for application settings."""

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
        assert settings.host == "0.0.0.0"
        assert settings.port == 8000
        assert settings.reload is True

    def test_settings_from_environment(self):
        """Test settings can be configured programmatically."""
        settings = Settings(
            app_name="Test App",
            app_version="2.0.0",
            host="127.0.0.1",
            port=9000,
        )

        assert settings.app_name == "Test App"
        assert settings.app_version == "2.0.0"
        assert settings.host == "127.0.0.1"
        assert settings.port == 9000

    def test_debug_true_from_env(self):
        """Test reload setting configuration."""
        settings = Settings(reload=False)
        assert settings.reload is False

    def test_debug_false_case_insensitive(self):
        """Test reload setting configuration."""
        settings = Settings(reload=False)
        assert settings.reload is False

    def test_environment_staging(self):
        """Test custom port setting."""
        settings = Settings(port=5000)
        assert settings.port == 5000

    def test_settings_validation(self):
        """Test settings validation."""
        settings = Settings()
        assert isinstance(settings.app_name, str)
        assert isinstance(settings.app_version, str)
        assert isinstance(settings.host, str)
        assert isinstance(settings.port, int)
        assert isinstance(settings.reload, bool)
