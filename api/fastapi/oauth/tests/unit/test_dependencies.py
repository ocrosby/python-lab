"""Unit tests for DI factory functions in dependencies.py."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

import fastapi_oauth_example.infrastructure.di.dependencies as deps_module
from fastapi_oauth_example.adapters.outbound.persistence.postgres_user_repository import (  # noqa: E501
    PostgresUserRepository,
)
from fastapi_oauth_example.adapters.outbound.persistence.token_repositories import (
    EmailVerificationTokenRepository,
    PasswordResetTokenRepository,
    RefreshTokenRepository,
    SessionRepository,
)
from fastapi_oauth_example.application.services.email_service import ConsoleEmailService
from fastapi_oauth_example.application.use_cases.email_verification_use_case import (
    SendEmailVerificationUseCase,
    VerifyEmailUseCase,
)
from fastapi_oauth_example.application.use_cases.login_user_use_case import (
    LoginUserUseCase,
)
from fastapi_oauth_example.application.use_cases.logout_use_case import LogoutUseCase
from fastapi_oauth_example.application.use_cases.mfa_use_cases import (
    EnableMFAUseCase,
    SetupMFAUseCase,
)
from fastapi_oauth_example.application.use_cases.password_reset_use_case import (
    RequestPasswordResetUseCase,
    ResetPasswordUseCase,
)
from fastapi_oauth_example.application.use_cases.refresh_token_use_case import (
    RefreshTokenUseCase,
)
from fastapi_oauth_example.application.use_cases.register_user_use_case import (
    RegisterUserUseCase,
)
from fastapi_oauth_example.application.use_cases.session_use_cases import (
    ListSessionsUseCase,
    RevokeSessionUseCase,
)
from fastapi_oauth_example.application.use_cases.verify_token_use_case import (
    VerifyTokenUseCase,
)
from fastapi_oauth_example.infrastructure.di.dependencies import (
    get_account_lockout_service,
    get_audit_logger,
    get_current_user,
    get_db_session,
    get_email_service,
    get_email_verification_token_repository,
    get_enable_mfa_use_case,
    get_jwt_handler,
    get_list_sessions_use_case,
    get_login_user_use_case,
    get_logout_use_case,
    get_mfa_service,
    get_password_hasher,
    get_password_reset_token_repository,
    get_refresh_token_repository,
    get_refresh_token_use_case,
    get_register_user_use_case,
    get_request_password_reset_use_case,
    get_reset_password_use_case,
    get_revoke_session_use_case,
    get_send_email_verification_use_case,
    get_session_repository,
    get_setup_mfa_use_case,
    get_token_blacklist_service,
    get_user_repository,
    get_verify_email_use_case,
    get_verify_token_use_case,
)
from fastapi_oauth_example.infrastructure.security.account_lockout import (
    AccountLockoutService,
)
from fastapi_oauth_example.infrastructure.security.audit_logger import AuditLogger
from fastapi_oauth_example.infrastructure.security.jwt_handler import JWTHandler
from fastapi_oauth_example.infrastructure.security.mfa_service import MFAService
from fastapi_oauth_example.infrastructure.security.password_hasher import PasswordHasher
from fastapi_oauth_example.infrastructure.security.token_blacklist import (
    TokenBlacklistService,
)

_CRYPT_PATH = (
    "fastapi_oauth_example.infrastructure.security.password_hasher.CryptContext"
)


@pytest.mark.unit
class TestSimpleFactories:
    def test_get_jwt_handler_returns_instance(self):
        assert isinstance(get_jwt_handler(), JWTHandler)

    def test_get_account_lockout_service_returns_instance(self):
        assert isinstance(get_account_lockout_service(), AccountLockoutService)

    def test_get_mfa_service_returns_instance(self):
        assert isinstance(get_mfa_service(), MFAService)

    def test_get_audit_logger_returns_instance(self):
        assert isinstance(get_audit_logger(), AuditLogger)

    def test_get_token_blacklist_service_returns_instance(self):
        assert isinstance(get_token_blacklist_service(), TokenBlacklistService)

    def test_get_email_service_returns_console_instance(self):
        assert isinstance(get_email_service(), ConsoleEmailService)

    def test_get_password_hasher_returns_instance(self):
        with patch(_CRYPT_PATH, return_value=MagicMock()):
            result = get_password_hasher()
        assert isinstance(result, PasswordHasher)


@pytest.mark.unit
class TestRepositoryFactories:
    def test_get_user_repository(self):
        assert isinstance(get_user_repository(MagicMock()), PostgresUserRepository)

    def test_get_refresh_token_repository(self):
        assert isinstance(
            get_refresh_token_repository(MagicMock()), RefreshTokenRepository
        )

    def test_get_password_reset_token_repository(self):
        assert isinstance(
            get_password_reset_token_repository(MagicMock()),
            PasswordResetTokenRepository,
        )

    def test_get_email_verification_token_repository(self):
        assert isinstance(
            get_email_verification_token_repository(MagicMock()),
            EmailVerificationTokenRepository,
        )

    def test_get_session_repository(self):
        assert isinstance(get_session_repository(MagicMock()), SessionRepository)


@pytest.mark.unit
class TestUseCaseFactories:
    def test_get_register_user_use_case(self):
        result = get_register_user_use_case(MagicMock(), MagicMock())
        assert isinstance(result, RegisterUserUseCase)

    def test_get_login_user_use_case(self):
        result = get_login_user_use_case(
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
        )
        assert isinstance(result, LoginUserUseCase)

    def test_get_verify_token_use_case(self):
        result = get_verify_token_use_case(
            MagicMock(), MagicMock(), MagicMock(), MagicMock()
        )
        assert isinstance(result, VerifyTokenUseCase)

    def test_get_logout_use_case(self):
        result = get_logout_use_case(
            MagicMock(), MagicMock(), MagicMock(), MagicMock(), MagicMock()
        )
        assert isinstance(result, LogoutUseCase)

    def test_get_refresh_token_use_case(self):
        result = get_refresh_token_use_case(MagicMock(), MagicMock(), MagicMock())
        assert isinstance(result, RefreshTokenUseCase)

    def test_get_request_password_reset_use_case(self):
        result = get_request_password_reset_use_case(
            MagicMock(), MagicMock(), MagicMock()
        )
        assert isinstance(result, RequestPasswordResetUseCase)

    def test_get_reset_password_use_case(self):
        result = get_reset_password_use_case(MagicMock(), MagicMock(), MagicMock())
        assert isinstance(result, ResetPasswordUseCase)

    def test_get_send_email_verification_use_case(self):
        result = get_send_email_verification_use_case(
            MagicMock(), MagicMock(), MagicMock()
        )
        assert isinstance(result, SendEmailVerificationUseCase)

    def test_get_verify_email_use_case(self):
        result = get_verify_email_use_case(MagicMock(), MagicMock())
        assert isinstance(result, VerifyEmailUseCase)

    def test_get_setup_mfa_use_case(self):
        result = get_setup_mfa_use_case(MagicMock(), MagicMock())
        assert isinstance(result, SetupMFAUseCase)

    def test_get_enable_mfa_use_case(self):
        result = get_enable_mfa_use_case(MagicMock(), MagicMock())
        assert isinstance(result, EnableMFAUseCase)

    def test_get_list_sessions_use_case(self):
        result = get_list_sessions_use_case(MagicMock())
        assert isinstance(result, ListSessionsUseCase)

    def test_get_revoke_session_use_case(self):
        result = get_revoke_session_use_case(MagicMock(), MagicMock())
        assert isinstance(result, RevokeSessionUseCase)


@pytest.mark.unit
class TestGetDbSession:
    async def test_get_db_session_yields_session(self):
        mock_session = MagicMock()

        async def _fake():
            yield mock_session

        with patch.object(deps_module.database, "get_session", return_value=_fake()):
            sessions = []
            async for s in get_db_session():
                sessions.append(s)
        assert sessions[0] is mock_session


@pytest.mark.unit
class TestGetCurrentUser:
    async def test_returns_result_of_execute(self):
        mock_uc = MagicMock()
        mock_uc.execute = AsyncMock(return_value="user_dto")
        result = await get_current_user("access_token", mock_uc)
        assert result == "user_dto"
        mock_uc.execute.assert_called_once_with("access_token")
