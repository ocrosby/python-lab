"""Unit tests for RegisterUserUseCase."""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from fastapi_oauth_example.application.dto.user_dto import (
    UserRegistrationDTO,
    UserResponseDTO,
)
from fastapi_oauth_example.application.use_cases.register_user_use_case import (
    RegisterUserUseCase,
)
from fastapi_oauth_example.domain.entities.user import User
from fastapi_oauth_example.domain.value_objects.email import Email
from fastapi_oauth_example.domain.value_objects.user_id import UserId


def make_user():
    now = datetime.utcnow()
    return User(
        id=UserId(value=uuid4()),
        email=Email(value="new@example.com"),
        username="newuser",
        hashed_password="hashed",
        is_active=True,
        is_verified=False,
        mfa_enabled=False,
        created_at=now,
        updated_at=now,
    )


@pytest.fixture
def repo():
    r = MagicMock()
    r.exists_by_email = AsyncMock(return_value=False)
    r.exists_by_username = AsyncMock(return_value=False)
    r.create = AsyncMock(return_value=make_user())
    return r


@pytest.fixture
def hasher():
    h = MagicMock()
    h.hash = MagicMock(return_value="hashed_password")
    return h


@pytest.mark.unit
class TestRegisterUserUseCase:
    async def test_returns_user_response_dto(self, repo, hasher):
        use_case = RegisterUserUseCase(repo, hasher)
        dto = UserRegistrationDTO(
            email="new@example.com", username="newuser", password="pass"
        )
        result = await use_case.execute(dto)
        assert isinstance(result, UserResponseDTO)
        assert result.username == "newuser"

    async def test_response_includes_mfa_enabled(self, repo, hasher):
        use_case = RegisterUserUseCase(repo, hasher)
        dto = UserRegistrationDTO(
            email="new@example.com", username="newuser", password="pass"
        )
        result = await use_case.execute(dto)
        assert result.mfa_enabled is False

    async def test_raises_when_email_taken(self, repo, hasher):
        repo.exists_by_email = AsyncMock(return_value=True)
        use_case = RegisterUserUseCase(repo, hasher)
        dto = UserRegistrationDTO(
            email="taken@example.com", username="user", password="pass"
        )
        with pytest.raises(ValueError, match="Email already registered"):
            await use_case.execute(dto)

    async def test_raises_when_username_taken(self, repo, hasher):
        repo.exists_by_username = AsyncMock(return_value=True)
        use_case = RegisterUserUseCase(repo, hasher)
        dto = UserRegistrationDTO(
            email="new@example.com", username="taken", password="pass"
        )
        with pytest.raises(ValueError, match="Username already taken"):
            await use_case.execute(dto)

    async def test_password_is_hashed(self, repo, hasher):
        use_case = RegisterUserUseCase(repo, hasher)
        dto = UserRegistrationDTO(
            email="new@example.com", username="newuser", password="secret"
        )
        await use_case.execute(dto)
        hasher.hash.assert_called_once_with("secret")
