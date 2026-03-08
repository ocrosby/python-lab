"""Unit tests for AccountLockoutService."""

from datetime import datetime, timedelta
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from fastapi_oauth_example.domain.entities.user import User
from fastapi_oauth_example.domain.value_objects.email import Email
from fastapi_oauth_example.domain.value_objects.user_id import UserId
from fastapi_oauth_example.infrastructure.security.account_lockout import (
    AccountLockoutService,
)


def make_user(**kwargs):
    defaults = {
        "id": UserId(value=uuid4()),
        "email": Email(value="u@example.com"),
        "username": "user",
        "hashed_password": "hashed",
    }
    defaults.update(kwargs)
    return User(**defaults)


@pytest.fixture
def svc():
    return AccountLockoutService(max_attempts=3, lockout_duration_minutes=15)


@pytest.mark.unit
class TestAccountLockoutService:
    def test_is_locked_false_when_no_lockout(self, svc):
        user = make_user()
        assert svc.is_locked(user) is False

    def test_is_locked_true_when_locked_in_future(self, svc):
        user = make_user(locked_until=datetime.utcnow() + timedelta(minutes=10))
        assert svc.is_locked(user) is True

    def test_is_locked_false_when_lockout_expired(self, svc):
        user = make_user(locked_until=datetime.utcnow() - timedelta(minutes=1))
        assert svc.is_locked(user) is False

    async def test_record_failed_attempt_increments_counter(self, svc):
        user = make_user()
        repo = AsyncMock()
        repo.update = AsyncMock()
        await svc.record_failed_attempt(user, repo)
        assert user.failed_login_attempts == 1
        repo.update.assert_called_once_with(user)

    async def test_record_failed_attempt_sets_lockout_at_max(self, svc):
        user = make_user(failed_login_attempts=2)
        repo = AsyncMock()
        repo.update = AsyncMock()
        await svc.record_failed_attempt(user, repo)
        assert user.failed_login_attempts == 3
        assert user.locked_until is not None
        assert user.locked_until > datetime.utcnow()

    async def test_reset_failed_attempts_clears_counter(self, svc):
        user = make_user(
            failed_login_attempts=3,
            locked_until=datetime.utcnow() + timedelta(minutes=5),
        )
        repo = AsyncMock()
        repo.update = AsyncMock()
        await svc.reset_failed_attempts(user, repo)
        assert user.failed_login_attempts == 0
        assert user.locked_until is None
        repo.update.assert_called_once_with(user)
