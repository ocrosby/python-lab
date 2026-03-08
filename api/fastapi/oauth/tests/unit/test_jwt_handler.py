"""Unit tests for JWTHandler."""

from datetime import timedelta

import pytest

from fastapi_oauth_example.infrastructure.security.jwt_handler import JWTHandler

SECRET = "test-secret-key"


@pytest.fixture
def handler():
    return JWTHandler(secret_key=SECRET, algorithm="HS256")


@pytest.mark.unit
class TestJWTHandler:
    def test_create_access_token_returns_string(self, handler):
        token = handler.create_access_token(data={"sub": "alice"})
        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_refresh_token_returns_string(self, handler):
        token = handler.create_refresh_token(data={"sub": "alice"})
        assert isinstance(token, str)

    def test_access_token_type_is_access(self, handler):
        token = handler.create_access_token(data={"sub": "alice"})
        payload = handler.decode_token(token)
        assert payload["type"] == "access"

    def test_refresh_token_type_is_refresh(self, handler):
        token = handler.create_refresh_token(data={"sub": "alice"})
        payload = handler.decode_token(token)
        assert payload["type"] == "refresh"

    def test_decode_access_token_returns_sub(self, handler):
        token = handler.create_access_token(data={"sub": "alice"})
        payload = handler.decode_token(token)
        assert payload["sub"] == "alice"

    def test_decode_invalid_token_returns_none(self, handler):
        result = handler.decode_token("not.a.token")
        assert result is None

    def test_decode_tampered_token_returns_none(self, handler):
        token = handler.create_access_token(data={"sub": "alice"})
        tampered = token[:-5] + "XXXXX"
        assert handler.decode_token(tampered) is None

    def test_decode_expired_token_returns_none(self, handler):
        token = handler.create_access_token(
            data={"sub": "alice"}, expires_delta=timedelta(seconds=-1)
        )
        assert handler.decode_token(token) is None

    def test_token_from_different_secret_returns_none(self, handler):
        other = JWTHandler(secret_key="other-secret")
        token = other.create_access_token(data={"sub": "alice"})
        assert handler.decode_token(token) is None
