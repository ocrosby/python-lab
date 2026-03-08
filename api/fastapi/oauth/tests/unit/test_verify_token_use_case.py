"""Unit tests for VerifyTokenUseCase."""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from fastapi_oauth_example.application.dto.user_dto import UserResponseDTO
from fastapi_oauth_example.application.use_cases.verify_token_use_case import (
    VerifyTokenUseCase,
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
        "is_active": True,
        "is_verified": True,
        "mfa_enabled": False,
        "created_at": now,
        "updated_at": now,
    }
    defaults.update(kwargs)
    return User(**defaults)


@pytest.fixture
def deps():
    repo = MagicMock()
    repo.get_by_username = AsyncMock(return_value=make_user())

    jwt = MagicMock()
    jwt.decode_token = MagicMock(return_value={"sub": "alice", "type": "access"})

    blacklist = MagicMock()
    blacklist.is_blacklisted = AsyncMock(return_value=False)

    session = MagicMock()

    return {
        "user_repository": repo,
        "jwt_handler": jwt,
        "token_blacklist": blacklist,
        "session": session,
    }


@pytest.mark.unit
class TestVerifyTokenUseCase:
    async def test_returns_user_response_dto(self, deps):
        uc = VerifyTokenUseCase(**deps)
        result = await uc.execute("valid_token")
        assert isinstance(result, UserResponseDTO)
        assert result.username == "alice"

    async def test_includes_mfa_enabled(self, deps):
        deps["user_repository"].get_by_username = AsyncMock(
            return_value=make_user(mfa_enabled=True)
        )
        uc = VerifyTokenUseCase(**deps)
        result = await uc.execute("valid_token")
        assert result.mfa_enabled is True

    async def test_raises_for_blacklisted_token(self, deps):
        deps["token_blacklist"].is_blacklisted = AsyncMock(return_value=True)
        uc = VerifyTokenUseCase(**deps)
        with pytest.raises(ValueError, match="Token has been revoked"):
            await uc.execute("blacklisted_token")

    async def test_raises_for_invalid_token(self, deps):
        deps["jwt_handler"].decode_token = MagicMock(return_value=None)
        uc = VerifyTokenUseCase(**deps)
        with pytest.raises(ValueError, match="Invalid token"):
            await uc.execute("bad_token")

    async def test_raises_for_missing_sub(self, deps):
        deps["jwt_handler"].decode_token = MagicMock(return_value={"type": "access"})
        uc = VerifyTokenUseCase(**deps)
        with pytest.raises(ValueError, match="Invalid token payload"):
            await uc.execute("no_sub_token")

    async def test_raises_for_unknown_user(self, deps):
        deps["user_repository"].get_by_username = AsyncMock(return_value=None)
        uc = VerifyTokenUseCase(**deps)
        with pytest.raises(ValueError, match="User not found"):
            await uc.execute("valid_token")
