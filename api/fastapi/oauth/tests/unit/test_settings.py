"""Unit tests for application settings."""

import pytest

from fastapi_oauth_example.infrastructure.config.settings import Settings


@pytest.mark.unit
class TestSettings:
    def test_default_algorithm(self):
        s = Settings()
        assert s.algorithm == "HS256"

    def test_default_access_token_expire_minutes(self):
        s = Settings()
        assert s.access_token_expire_minutes == 30

    def test_default_refresh_token_expire_days(self):
        s = Settings()
        assert s.refresh_token_expire_days == 7

    def test_default_max_login_attempts(self):
        s = Settings()
        assert s.max_login_attempts == 5

    def test_default_lockout_duration_minutes(self):
        s = Settings()
        assert s.lockout_duration_minutes == 15

    def test_default_rate_limit(self):
        s = Settings()
        assert s.rate_limit_requests_per_minute == 5

    def test_database_url_contains_asyncpg(self):
        s = Settings()
        assert "asyncpg" in s.database_url

    def test_cors_origins_is_list(self):
        s = Settings()
        assert isinstance(s.cors_origins, list)
