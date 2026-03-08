"""Unit tests for MFA use cases."""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from fastapi_oauth_example.application.dto.user_dto import (
    MFASetupResponseDTO,
    MFAVerifyDTO,
)
from fastapi_oauth_example.application.use_cases.mfa_use_cases import (
    EnableMFAUseCase,
    SetupMFAUseCase,
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
        "mfa_enabled": False,
        "mfa_secret": None,
        "created_at": now,
        "updated_at": now,
    }
    defaults.update(kwargs)
    return User(**defaults)


@pytest.mark.unit
class TestSetupMFAUseCase:
    async def test_returns_mfa_setup_response_dto(self):
        repo = MagicMock()
        repo.get_by_id = AsyncMock(return_value=make_user())
        repo.update = AsyncMock()
        mfa_svc = MagicMock()
        mfa_svc.generate_secret = MagicMock(return_value="SECRETKEY")
        mfa_svc.generate_qr_code = MagicMock(return_value="otpauth://totp/...")

        uc = SetupMFAUseCase(repo, mfa_svc)
        result = await uc.execute(UserId(value=uuid4()))

        assert isinstance(result, MFASetupResponseDTO)
        assert result.secret == "SECRETKEY"

    async def test_saves_secret_to_user(self):
        user = make_user()
        repo = MagicMock()
        repo.get_by_id = AsyncMock(return_value=user)
        repo.update = AsyncMock()
        mfa_svc = MagicMock()
        mfa_svc.generate_secret = MagicMock(return_value="NEWSECRET")
        mfa_svc.generate_qr_code = MagicMock(return_value="otpauth://...")

        uc = SetupMFAUseCase(repo, mfa_svc)
        await uc.execute(UserId(value=uuid4()))

        assert user.mfa_secret == "NEWSECRET"
        repo.update.assert_called_once_with(user)

    async def test_raises_when_user_not_found(self):
        repo = MagicMock()
        repo.get_by_id = AsyncMock(return_value=None)
        mfa_svc = MagicMock()

        uc = SetupMFAUseCase(repo, mfa_svc)
        with pytest.raises(ValueError, match="User not found"):
            await uc.execute(UserId(value=uuid4()))


@pytest.mark.unit
class TestEnableMFAUseCase:
    async def test_enables_mfa_with_valid_code(self):
        user = make_user(mfa_secret="SECRET")
        repo = MagicMock()
        repo.get_by_id = AsyncMock(return_value=user)
        repo.update = AsyncMock()
        mfa_svc = MagicMock()
        mfa_svc.verify_code = MagicMock(return_value=True)

        uc = EnableMFAUseCase(repo, mfa_svc)
        await uc.execute(UserId(value=uuid4()), MFAVerifyDTO(code="123456"))

        assert user.mfa_enabled is True
        repo.update.assert_called_once_with(user)

    async def test_raises_when_user_not_found(self):
        repo = MagicMock()
        repo.get_by_id = AsyncMock(return_value=None)
        mfa_svc = MagicMock()

        uc = EnableMFAUseCase(repo, mfa_svc)
        with pytest.raises(ValueError, match="User not found"):
            await uc.execute(UserId(value=uuid4()), MFAVerifyDTO(code="123456"))

    async def test_raises_when_mfa_not_set_up(self):
        repo = MagicMock()
        repo.get_by_id = AsyncMock(return_value=make_user(mfa_secret=None))
        mfa_svc = MagicMock()

        uc = EnableMFAUseCase(repo, mfa_svc)
        with pytest.raises(ValueError, match="MFA not set up"):
            await uc.execute(UserId(value=uuid4()), MFAVerifyDTO(code="123456"))

    async def test_raises_for_invalid_mfa_code(self):
        repo = MagicMock()
        repo.get_by_id = AsyncMock(return_value=make_user(mfa_secret="SECRET"))
        mfa_svc = MagicMock()
        mfa_svc.verify_code = MagicMock(return_value=False)

        uc = EnableMFAUseCase(repo, mfa_svc)
        with pytest.raises(ValueError, match="Invalid MFA code"):
            await uc.execute(UserId(value=uuid4()), MFAVerifyDTO(code="000000"))
