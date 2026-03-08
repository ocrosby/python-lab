"""Unit tests for RefreshTokenUseCase."""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from fastapi_oauth_example.application.dto.user_dto import RefreshTokenDTO, TokenDTO
from fastapi_oauth_example.application.use_cases.refresh_token_use_case import (
    RefreshTokenUseCase,
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
        "created_at": now,
        "updated_at": now,
    }
    defaults.update(kwargs)
    return User(**defaults)


def make_rt(revoked=False):
    rt = MagicMock()
    rt.revoked = revoked
    return rt


@pytest.fixture
def deps():
    repo = MagicMock()
    repo.get_by_username = AsyncMock(return_value=make_user())

    jwt = MagicMock()
    jwt.decode_token = MagicMock(return_value={"sub": "alice", "type": "refresh"})
    jwt.create_access_token = MagicMock(return_value="new_access_tok")

    refresh_repo = MagicMock()
    refresh_repo.get_by_token = AsyncMock(return_value=make_rt())

    return {
        "user_repository": repo,
        "jwt_handler": jwt,
        "refresh_token_repository": refresh_repo,
    }


@pytest.mark.unit
class TestRefreshTokenUseCase:
    async def test_returns_token_dto(self, deps):
        uc = RefreshTokenUseCase(**deps)
        result = await uc.execute(RefreshTokenDTO(refresh_token="ref_tok"))
        assert isinstance(result, TokenDTO)
        assert result.access_token == "new_access_tok"

    async def test_refresh_token_unchanged_in_response(self, deps):
        uc = RefreshTokenUseCase(**deps)
        result = await uc.execute(RefreshTokenDTO(refresh_token="ref_tok"))
        assert result.refresh_token == "ref_tok"

    async def test_raises_for_invalid_token_decode(self, deps):
        deps["jwt_handler"].decode_token = MagicMock(return_value=None)
        uc = RefreshTokenUseCase(**deps)
        with pytest.raises(ValueError, match="Invalid refresh token"):
            await uc.execute(RefreshTokenDTO(refresh_token="bad"))

    async def test_raises_for_wrong_token_type(self, deps):
        deps["jwt_handler"].decode_token = MagicMock(
            return_value={"sub": "alice", "type": "access"}
        )
        uc = RefreshTokenUseCase(**deps)
        with pytest.raises(ValueError, match="Invalid refresh token"):
            await uc.execute(RefreshTokenDTO(refresh_token="wrong_type"))

    async def test_raises_for_revoked_token(self, deps):
        deps["refresh_token_repository"].get_by_token = AsyncMock(
            return_value=make_rt(revoked=True)
        )
        uc = RefreshTokenUseCase(**deps)
        with pytest.raises(ValueError, match="Refresh token has been revoked"):
            await uc.execute(RefreshTokenDTO(refresh_token="revoked"))

    async def test_raises_when_token_not_in_db(self, deps):
        deps["refresh_token_repository"].get_by_token = AsyncMock(return_value=None)
        uc = RefreshTokenUseCase(**deps)
        with pytest.raises(ValueError, match="Refresh token has been revoked"):
            await uc.execute(RefreshTokenDTO(refresh_token="missing"))

    async def test_raises_for_unknown_user(self, deps):
        deps["user_repository"].get_by_username = AsyncMock(return_value=None)
        uc = RefreshTokenUseCase(**deps)
        with pytest.raises(ValueError, match="Invalid user"):
            await uc.execute(RefreshTokenDTO(refresh_token="ref_tok"))

    async def test_raises_for_inactive_user(self, deps):
        deps["user_repository"].get_by_username = AsyncMock(
            return_value=make_user(is_active=False)
        )
        uc = RefreshTokenUseCase(**deps)
        with pytest.raises(ValueError, match="Invalid user"):
            await uc.execute(RefreshTokenDTO(refresh_token="ref_tok"))
