"""Unit tests for email verification use cases."""

from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from fastapi_oauth_example.application.dto.user_dto import EmailVerificationDTO
from fastapi_oauth_example.application.use_cases.email_verification_use_case import (
    SendEmailVerificationUseCase,
    VerifyEmailUseCase,
)
from fastapi_oauth_example.domain.entities.user import User
from fastapi_oauth_example.domain.value_objects.email import Email
from fastapi_oauth_example.domain.value_objects.user_id import UserId


def make_user(**kwargs):
    now = datetime.utcnow()
    defaults = {
        "id": UserId(value=uuid4()),
        "email": Email(value="u@example.com"),
        "username": "alice",
        "hashed_password": "hashed",
        "is_verified": False,
        "created_at": now,
        "updated_at": now,
    }
    defaults.update(kwargs)
    return User(**defaults)


def make_token_model(used=False, expires_delta=timedelta(hours=24)):
    m = MagicMock()
    m.user_id = uuid4()
    m.used = used
    m.expires_at = datetime.utcnow() + expires_delta
    return m


@pytest.mark.unit
class TestSendEmailVerificationUseCase:
    async def test_persists_token_and_sends_email(self):
        repo = MagicMock()
        repo.get_by_id = AsyncMock(return_value=make_user())
        email_svc = MagicMock()
        email_svc.send_verification_email = AsyncMock()
        token_repo = MagicMock()
        token_repo.create = AsyncMock()

        uc = SendEmailVerificationUseCase(repo, email_svc, token_repo)
        await uc.execute(UserId(value=uuid4()))

        token_repo.create.assert_called_once()
        email_svc.send_verification_email.assert_called_once()

    async def test_raises_when_user_not_found(self):
        repo = MagicMock()
        repo.get_by_id = AsyncMock(return_value=None)
        email_svc = MagicMock()
        token_repo = MagicMock()

        uc = SendEmailVerificationUseCase(repo, email_svc, token_repo)
        with pytest.raises(ValueError, match="User not found"):
            await uc.execute(UserId(value=uuid4()))

    async def test_raises_when_already_verified(self):
        repo = MagicMock()
        repo.get_by_id = AsyncMock(return_value=make_user(is_verified=True))
        email_svc = MagicMock()
        token_repo = MagicMock()

        uc = SendEmailVerificationUseCase(repo, email_svc, token_repo)
        with pytest.raises(ValueError, match="User already verified"):
            await uc.execute(UserId(value=uuid4()))


@pytest.mark.unit
class TestVerifyEmailUseCase:
    async def test_marks_user_as_verified(self):
        user = make_user()
        repo = MagicMock()
        repo.get_by_id = AsyncMock(return_value=user)
        repo.update = AsyncMock()
        token_repo = MagicMock()
        token_repo.get_by_token = AsyncMock(return_value=make_token_model())
        token_repo.mark_as_used = AsyncMock()

        uc = VerifyEmailUseCase(repo, token_repo)
        await uc.execute(EmailVerificationDTO(token="tok"))

        assert user.is_verified is True
        repo.update.assert_called_once()
        token_repo.mark_as_used.assert_called_once_with("tok")

    async def test_raises_for_invalid_token(self):
        repo = MagicMock()
        token_repo = MagicMock()
        token_repo.get_by_token = AsyncMock(return_value=None)

        uc = VerifyEmailUseCase(repo, token_repo)
        with pytest.raises(ValueError, match="Invalid or expired token"):
            await uc.execute(EmailVerificationDTO(token="bad"))

    async def test_raises_for_used_token(self):
        repo = MagicMock()
        token_repo = MagicMock()
        token_repo.get_by_token = AsyncMock(return_value=make_token_model(used=True))

        uc = VerifyEmailUseCase(repo, token_repo)
        with pytest.raises(ValueError, match="Token already used"):
            await uc.execute(EmailVerificationDTO(token="used"))

    async def test_raises_for_expired_token(self):
        repo = MagicMock()
        token_repo = MagicMock()
        token_repo.get_by_token = AsyncMock(
            return_value=make_token_model(expires_delta=timedelta(hours=-1))
        )

        uc = VerifyEmailUseCase(repo, token_repo)
        with pytest.raises(ValueError, match="Token has expired"):
            await uc.execute(EmailVerificationDTO(token="expired"))

    async def test_raises_when_user_not_found(self):
        repo = MagicMock()
        repo.get_by_id = AsyncMock(return_value=None)
        token_repo = MagicMock()
        token_repo.get_by_token = AsyncMock(return_value=make_token_model())

        uc = VerifyEmailUseCase(repo, token_repo)
        with pytest.raises(ValueError, match="User not found"):
            await uc.execute(EmailVerificationDTO(token="tok"))
