"""Unit tests for PasswordHasher."""

from unittest.mock import MagicMock, patch

import pytest

from fastapi_oauth_example.infrastructure.security.password_hasher import PasswordHasher


@pytest.fixture
def mock_context():
    """Patch CryptContext to avoid real bcrypt backend initialisation."""
    ctx = MagicMock()
    ctx.hash = MagicMock(return_value="$2b$12$hashed_value")
    ctx.verify = MagicMock(return_value=True)
    with patch(
        "fastapi_oauth_example.infrastructure.security.password_hasher.CryptContext",
        return_value=ctx,
    ):
        yield ctx


@pytest.mark.unit
class TestPasswordHasher:
    def test_hash_returns_string(self, mock_context):
        hasher = PasswordHasher()
        result = hasher.hash("mypassword")
        assert isinstance(result, str)

    def test_hash_delegates_to_context(self, mock_context):
        hasher = PasswordHasher()
        hasher.hash("secret")
        mock_context.hash.assert_called_once_with("secret")

    def test_verify_returns_true_for_correct_password(self, mock_context):
        mock_context.verify = MagicMock(return_value=True)
        hasher = PasswordHasher()
        assert hasher.verify("correct", "$2b$12$hashed") is True

    def test_verify_returns_false_for_wrong_password(self, mock_context):
        mock_context.verify = MagicMock(return_value=False)
        hasher = PasswordHasher()
        assert hasher.verify("wrong", "$2b$12$hashed") is False

    def test_verify_delegates_to_context(self, mock_context):
        hasher = PasswordHasher()
        hasher.verify("plain", "hashed")
        mock_context.verify.assert_called_once_with("plain", "hashed")
