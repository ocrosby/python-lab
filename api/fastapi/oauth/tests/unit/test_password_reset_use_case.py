"""Unit tests for password reset use cases."""

from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from fastapi_oauth_example.application.dto.user_dto import (
    PasswordResetDTO,
    PasswordResetRequestDTO,
)
from fastapi_oauth_example.application.use_cases.password_reset_use_case import (
    RequestPasswordResetUseCase,
    ResetPasswordUseCase,
)
from fastapi_oauth_example.domain.entities.user import User
from fastapi_oauth_example.domain.value_objects.email import Email
from fastapi_oauth_example.domain.value_objects.user_id import UserId


def make_user():
    now = datetime.utcnow()
    return User(
        id=UserId(value=uuid4()),
        email=Email(value="u@example.com"),
        username="alice",
        hashed_password="hashed",
        created_at=now,
        updated_at=now,
    )


def make_token_model(used=False, expires_delta=timedelta(hours=1)):
    m = MagicMock()
    m.user_id = uuid4()
    m.used = used
    m.expires_at = datetime.utcnow() + expires_delta
    return m


@pytest.mark.unit
class TestRequestPasswordResetUseCase:
    async def test_creates_token_and_sends_email_when_user_exists(self):
        repo = MagicMock()
        repo.get_by_email = AsyncMock(return_value=make_user())
        email_svc = MagicMock()
        email_svc.send_password_reset_email = AsyncMock()
        token_repo = MagicMock()
        token_repo.create = AsyncMock()

        uc = RequestPasswordResetUseCase(repo, email_svc, token_repo)
        await uc.execute(PasswordResetRequestDTO(email="u@example.com"))

        token_repo.create.assert_called_once()
        email_svc.send_password_reset_email.assert_called_once()

    async def test_does_nothing_when_user_not_found(self):
        repo = MagicMock()
        repo.get_by_email = AsyncMock(return_value=None)
        email_svc = MagicMock()
        email_svc.send_password_reset_email = AsyncMock()
        token_repo = MagicMock()
        token_repo.create = AsyncMock()

        uc = RequestPasswordResetUseCase(repo, email_svc, token_repo)
        await uc.execute(PasswordResetRequestDTO(email="unknown@example.com"))

        token_repo.create.assert_not_called()
        email_svc.send_password_reset_email.assert_not_called()


@pytest.mark.unit
class TestResetPasswordUseCase:
    async def test_resets_password_for_valid_token(self):
        user = make_user()
        repo = MagicMock()
        repo.get_by_id = AsyncMock(return_value=user)
        repo.update = AsyncMock()
        hasher = MagicMock()
        hasher.hash = MagicMock(return_value="new_hashed")
        token_repo = MagicMock()
        token_repo.get_by_token = AsyncMock(return_value=make_token_model())
        token_repo.mark_as_used = AsyncMock()

        uc = ResetPasswordUseCase(repo, hasher, token_repo)
        await uc.execute(PasswordResetDTO(token="tok", new_password="newpass"))

        repo.update.assert_called_once()
        token_repo.mark_as_used.assert_called_once_with("tok")

    async def test_raises_for_invalid_token(self):
        repo = MagicMock()
        hasher = MagicMock()
        token_repo = MagicMock()
        token_repo.get_by_token = AsyncMock(return_value=None)

        uc = ResetPasswordUseCase(repo, hasher, token_repo)
        with pytest.raises(ValueError, match="Invalid or expired token"):
            await uc.execute(PasswordResetDTO(token="bad", new_password="newpass"))

    async def test_raises_for_used_token(self):
        repo = MagicMock()
        hasher = MagicMock()
        token_repo = MagicMock()
        token_repo.get_by_token = AsyncMock(return_value=make_token_model(used=True))

        uc = ResetPasswordUseCase(repo, hasher, token_repo)
        with pytest.raises(ValueError, match="Token already used"):
            await uc.execute(PasswordResetDTO(token="used", new_password="newpass"))

    async def test_raises_for_expired_token(self):
        repo = MagicMock()
        hasher = MagicMock()
        token_repo = MagicMock()
        token_repo.get_by_token = AsyncMock(
            return_value=make_token_model(expires_delta=timedelta(hours=-1))
        )

        uc = ResetPasswordUseCase(repo, hasher, token_repo)
        with pytest.raises(ValueError, match="Token has expired"):
            await uc.execute(PasswordResetDTO(token="expired", new_password="newpass"))

    async def test_raises_when_user_not_found(self):
        repo = MagicMock()
        repo.get_by_id = AsyncMock(return_value=None)
        hasher = MagicMock()
        token_repo = MagicMock()
        token_repo.get_by_token = AsyncMock(return_value=make_token_model())

        uc = ResetPasswordUseCase(repo, hasher, token_repo)
        with pytest.raises(ValueError, match="User not found"):
            await uc.execute(PasswordResetDTO(token="tok", new_password="newpass"))
