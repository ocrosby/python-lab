"""Unit tests for LoginUserUseCase."""

from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from fastapi_oauth_example.application.dto.user_dto import TokenDTO, UserLoginDTO
from fastapi_oauth_example.application.use_cases.login_user_use_case import (
    LoginUserUseCase,
)
from fastapi_oauth_example.domain.entities.user import User
from fastapi_oauth_example.domain.value_objects.email import Email
from fastapi_oauth_example.domain.value_objects.user_id import UserId


def make_user(**kwargs):
    defaults = {
        "id": UserId(value=uuid4()),
        "email": Email(value="u@example.com"),
        "username": "alice",
        "hashed_password": "hashed",
        "is_active": True,
        "mfa_enabled": False,
        "failed_login_attempts": 0,
        "locked_until": None,
    }
    defaults.update(kwargs)
    return User(**defaults)


def make_rt():
    rt = MagicMock()
    rt.id = uuid4()
    return rt


@pytest.fixture
def deps():
    repo = MagicMock()
    repo.get_by_username = AsyncMock(return_value=make_user())
    repo.update = AsyncMock()

    hasher = MagicMock()
    hasher.verify = MagicMock(return_value=True)

    jwt = MagicMock()
    jwt.create_access_token = MagicMock(return_value="access_tok")
    jwt.create_refresh_token = MagicMock(return_value="refresh_tok")

    lockout = MagicMock()
    lockout.is_locked = MagicMock(return_value=False)
    lockout.record_failed_attempt = AsyncMock()
    lockout.reset_failed_attempts = AsyncMock()

    mfa_svc = MagicMock()
    mfa_svc.verify_code = MagicMock(return_value=True)

    refresh_repo = MagicMock()
    refresh_repo.create = AsyncMock(return_value=make_rt())

    session_repo = MagicMock()
    session_repo.create = AsyncMock()

    audit = MagicMock()
    audit.log_event = AsyncMock()

    db_session = MagicMock()

    return {
        "user_repository": repo,
        "password_hasher": hasher,
        "jwt_handler": jwt,
        "lockout_service": lockout,
        "mfa_service": mfa_svc,
        "refresh_repo": refresh_repo,
        "session_repo": session_repo,
        "audit_logger": audit,
        "db_session": db_session,
    }


def make_use_case(deps):
    return LoginUserUseCase(**deps)


@pytest.mark.unit
class TestLoginUserUseCase:
    async def test_returns_token_dto_on_success(self, deps):
        uc = make_use_case(deps)
        dto = UserLoginDTO(username="alice", password="pass")
        result = await uc.execute(dto)
        assert isinstance(result, TokenDTO)
        assert result.access_token == "access_tok"
        assert result.refresh_token == "refresh_tok"

    async def test_raises_for_unknown_user(self, deps):
        deps["user_repository"].get_by_username = AsyncMock(return_value=None)
        uc = make_use_case(deps)
        with pytest.raises(ValueError, match="Invalid credentials"):
            await uc.execute(UserLoginDTO(username="nobody", password="pass"))

    async def test_raises_for_locked_account(self, deps):
        deps["lockout_service"].is_locked = MagicMock(return_value=True)
        uc = make_use_case(deps)
        with pytest.raises(ValueError, match="Account is locked"):
            await uc.execute(UserLoginDTO(username="alice", password="pass"))

    async def test_raises_for_wrong_password(self, deps):
        deps["password_hasher"].verify = MagicMock(return_value=False)
        uc = make_use_case(deps)
        with pytest.raises(ValueError, match="Invalid credentials"):
            await uc.execute(UserLoginDTO(username="alice", password="wrong"))

    async def test_records_failed_attempt_on_wrong_password(self, deps):
        deps["password_hasher"].verify = MagicMock(return_value=False)
        uc = make_use_case(deps)
        with pytest.raises(ValueError):
            await uc.execute(UserLoginDTO(username="alice", password="wrong"))
        deps["lockout_service"].record_failed_attempt.assert_called_once()

    async def test_raises_for_inactive_account(self, deps):
        deps["user_repository"].get_by_username = AsyncMock(
            return_value=make_user(is_active=False)
        )
        uc = make_use_case(deps)
        with pytest.raises(ValueError, match="Inactive account"):
            await uc.execute(UserLoginDTO(username="alice", password="pass"))

    async def test_raises_when_mfa_required_but_not_provided(self, deps):
        deps["user_repository"].get_by_username = AsyncMock(
            return_value=make_user(mfa_enabled=True, mfa_secret="SECRET")
        )
        uc = make_use_case(deps)
        with pytest.raises(ValueError, match="MFA code required"):
            await uc.execute(UserLoginDTO(username="alice", password="pass"))

    async def test_raises_for_invalid_mfa_code(self, deps):
        deps["user_repository"].get_by_username = AsyncMock(
            return_value=make_user(mfa_enabled=True, mfa_secret="SECRET")
        )
        deps["mfa_service"].verify_code = MagicMock(return_value=False)
        uc = make_use_case(deps)
        with pytest.raises(ValueError, match="Invalid MFA code"):
            await uc.execute(
                UserLoginDTO(username="alice", password="pass", mfa_code="000000")
            )

    async def test_passes_with_valid_mfa_code(self, deps):
        deps["user_repository"].get_by_username = AsyncMock(
            return_value=make_user(mfa_enabled=True, mfa_secret="SECRET")
        )
        deps["mfa_service"].verify_code = MagicMock(return_value=True)
        uc = make_use_case(deps)
        result = await uc.execute(
            UserLoginDTO(username="alice", password="pass", mfa_code="123456")
        )
        assert isinstance(result, TokenDTO)

    async def test_persists_refresh_token_and_session(self, deps):
        uc = make_use_case(deps)
        await uc.execute(UserLoginDTO(username="alice", password="pass"))
        deps["refresh_repo"].create.assert_called_once()
        deps["session_repo"].create.assert_called_once()

    async def test_logs_audit_event(self, deps):
        uc = make_use_case(deps)
        await uc.execute(UserLoginDTO(username="alice", password="pass"))
        deps["audit_logger"].log_event.assert_called_once()

    async def test_resets_failed_attempts_on_success(self, deps):
        uc = make_use_case(deps)
        await uc.execute(UserLoginDTO(username="alice", password="pass"))
        deps["lockout_service"].reset_failed_attempts.assert_called_once()

    async def test_passes_ip_and_user_agent_to_session(self, deps):
        uc = make_use_case(deps)
        await uc.execute(
            UserLoginDTO(username="alice", password="pass"),
            ip_address="1.2.3.4",
            user_agent="TestAgent",
        )
        deps["session_repo"].create.assert_called_once()
        call_args = deps["session_repo"].create.call_args
        assert call_args[0][2] == "1.2.3.4"
        assert call_args[0][3] == "TestAgent"
