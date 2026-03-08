"""Unit tests for domain entities."""

from uuid import uuid4

import pytest

from fastapi_oauth_example.domain.entities.user import User
from fastapi_oauth_example.domain.value_objects.email import Email
from fastapi_oauth_example.domain.value_objects.user_id import UserId


@pytest.mark.unit
class TestUser:
    def test_user_created_with_required_fields(self):
        user = User(
            id=UserId(value=uuid4()),
            email=Email(value="user@example.com"),
            username="testuser",
            hashed_password="hashed",
        )
        assert user.username == "testuser"
        assert str(user.email) == "user@example.com"

    def test_default_is_active_true(self):
        user = User(
            id=UserId(value=uuid4()),
            email=Email(value="a@b.com"),
            username="u",
            hashed_password="h",
        )
        assert user.is_active is True

    def test_default_is_verified_false(self):
        user = User(
            id=UserId(value=uuid4()),
            email=Email(value="a@b.com"),
            username="u",
            hashed_password="h",
        )
        assert user.is_verified is False

    def test_default_mfa_disabled(self):
        user = User(
            id=UserId(value=uuid4()),
            email=Email(value="a@b.com"),
            username="u",
            hashed_password="h",
        )
        assert user.mfa_enabled is False
        assert user.mfa_secret is None

    def test_default_failed_attempts_zero(self):
        user = User(
            id=UserId(value=uuid4()),
            email=Email(value="a@b.com"),
            username="u",
            hashed_password="h",
        )
        assert user.failed_login_attempts == 0

    def test_locked_until_defaults_none(self):
        user = User(
            id=UserId(value=uuid4()),
            email=Email(value="a@b.com"),
            username="u",
            hashed_password="h",
        )
        assert user.locked_until is None
