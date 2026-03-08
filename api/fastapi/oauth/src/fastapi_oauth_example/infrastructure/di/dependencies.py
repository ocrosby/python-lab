from collections.abc import AsyncGenerator

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi_oauth_example.adapters.outbound.persistence.database import Database
from fastapi_oauth_example.adapters.outbound.persistence.postgres_user_repository import (  # noqa: E501
    PostgresUserRepository,
)
from fastapi_oauth_example.adapters.outbound.persistence.token_repositories import (
    EmailVerificationTokenRepository,
    PasswordResetTokenRepository,
    RefreshTokenRepository,
    SessionRepository,
)
from fastapi_oauth_example.application.services.email_service import (
    ConsoleEmailService,
    EmailService,
)
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
from fastapi_oauth_example.infrastructure.config.settings import settings
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
from fastapi_oauth_example.ports.outbound.user_repository import UserRepository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

database = Database(settings.database_url)


async def get_db_session() -> AsyncGenerator[AsyncSession]:
    async for session in database.get_session():
        yield session


def get_password_hasher() -> PasswordHasher:
    return PasswordHasher()


def get_jwt_handler() -> JWTHandler:
    return JWTHandler(
        secret_key=settings.secret_key,
        algorithm=settings.algorithm,
        access_token_expire_minutes=settings.access_token_expire_minutes,
        refresh_token_expire_days=settings.refresh_token_expire_days,
    )


def get_account_lockout_service() -> AccountLockoutService:
    return AccountLockoutService(
        max_attempts=settings.max_login_attempts,
        lockout_duration_minutes=settings.lockout_duration_minutes,
    )


def get_mfa_service() -> MFAService:
    return MFAService()


def get_audit_logger() -> AuditLogger:
    return AuditLogger()


def get_token_blacklist_service() -> TokenBlacklistService:
    return TokenBlacklistService()


def get_email_service() -> EmailService:
    return ConsoleEmailService()


def get_user_repository(
    session: AsyncSession = Depends(get_db_session),
) -> UserRepository:
    return PostgresUserRepository(session)


def get_refresh_token_repository(
    session: AsyncSession = Depends(get_db_session),
) -> RefreshTokenRepository:
    return RefreshTokenRepository(session)


def get_password_reset_token_repository(
    session: AsyncSession = Depends(get_db_session),
) -> PasswordResetTokenRepository:
    return PasswordResetTokenRepository(session)


def get_email_verification_token_repository(
    session: AsyncSession = Depends(get_db_session),
) -> EmailVerificationTokenRepository:
    return EmailVerificationTokenRepository(session)


def get_session_repository(
    session: AsyncSession = Depends(get_db_session),
) -> SessionRepository:
    return SessionRepository(session)


def get_register_user_use_case(
    user_repository: UserRepository = Depends(get_user_repository),
    password_hasher: PasswordHasher = Depends(get_password_hasher),
) -> RegisterUserUseCase:
    return RegisterUserUseCase(user_repository, password_hasher)


def get_login_user_use_case(
    user_repository: UserRepository = Depends(get_user_repository),
    password_hasher: PasswordHasher = Depends(get_password_hasher),
    jwt_handler: JWTHandler = Depends(get_jwt_handler),
    lockout_service: AccountLockoutService = Depends(get_account_lockout_service),
    mfa_service: MFAService = Depends(get_mfa_service),
    refresh_repo: RefreshTokenRepository = Depends(get_refresh_token_repository),
    session_repo: SessionRepository = Depends(get_session_repository),
    audit_logger: AuditLogger = Depends(get_audit_logger),
    db_session: AsyncSession = Depends(get_db_session),
) -> LoginUserUseCase:
    return LoginUserUseCase(
        user_repository=user_repository,
        password_hasher=password_hasher,
        jwt_handler=jwt_handler,
        lockout_service=lockout_service,
        mfa_service=mfa_service,
        refresh_repo=refresh_repo,
        session_repo=session_repo,
        audit_logger=audit_logger,
        db_session=db_session,
        access_token_expire_minutes=settings.access_token_expire_minutes,
        refresh_token_expire_days=settings.refresh_token_expire_days,
    )


def get_verify_token_use_case(
    user_repository: UserRepository = Depends(get_user_repository),
    jwt_handler: JWTHandler = Depends(get_jwt_handler),
    token_blacklist: TokenBlacklistService = Depends(get_token_blacklist_service),
    db_session: AsyncSession = Depends(get_db_session),
) -> VerifyTokenUseCase:
    return VerifyTokenUseCase(user_repository, jwt_handler, token_blacklist, db_session)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    verify_token_use_case: VerifyTokenUseCase = Depends(get_verify_token_use_case),
):
    return await verify_token_use_case.execute(token)


def get_logout_use_case(
    token_blacklist: TokenBlacklistService = Depends(get_token_blacklist_service),
    refresh_repo: RefreshTokenRepository = Depends(get_refresh_token_repository),
    jwt_handler: JWTHandler = Depends(get_jwt_handler),
    audit_logger: AuditLogger = Depends(get_audit_logger),
    db_session: AsyncSession = Depends(get_db_session),
) -> LogoutUseCase:
    return LogoutUseCase(
        token_blacklist, refresh_repo, jwt_handler, audit_logger, db_session
    )


def get_refresh_token_use_case(
    user_repository: UserRepository = Depends(get_user_repository),
    jwt_handler: JWTHandler = Depends(get_jwt_handler),
    refresh_token_repository: RefreshTokenRepository = Depends(
        get_refresh_token_repository
    ),
) -> RefreshTokenUseCase:
    return RefreshTokenUseCase(
        user_repository,
        jwt_handler,
        refresh_token_repository,
        settings.access_token_expire_minutes,
    )


def get_request_password_reset_use_case(
    user_repository: UserRepository = Depends(get_user_repository),
    email_service: EmailService = Depends(get_email_service),
    token_repository: PasswordResetTokenRepository = Depends(
        get_password_reset_token_repository
    ),
) -> RequestPasswordResetUseCase:
    return RequestPasswordResetUseCase(
        user_repository,
        email_service,
        token_repository,
        settings.password_reset_token_expire_hours,
    )


def get_reset_password_use_case(
    user_repository: UserRepository = Depends(get_user_repository),
    password_hasher: PasswordHasher = Depends(get_password_hasher),
    token_repository: PasswordResetTokenRepository = Depends(
        get_password_reset_token_repository
    ),
) -> ResetPasswordUseCase:
    return ResetPasswordUseCase(user_repository, password_hasher, token_repository)


def get_send_email_verification_use_case(
    user_repository: UserRepository = Depends(get_user_repository),
    email_service: EmailService = Depends(get_email_service),
    token_repository: EmailVerificationTokenRepository = Depends(
        get_email_verification_token_repository
    ),
) -> SendEmailVerificationUseCase:
    return SendEmailVerificationUseCase(
        user_repository,
        email_service,
        token_repository,
        settings.email_verification_token_expire_hours,
    )


def get_verify_email_use_case(
    user_repository: UserRepository = Depends(get_user_repository),
    token_repository: EmailVerificationTokenRepository = Depends(
        get_email_verification_token_repository
    ),
) -> VerifyEmailUseCase:
    return VerifyEmailUseCase(user_repository, token_repository)


def get_setup_mfa_use_case(
    user_repository: UserRepository = Depends(get_user_repository),
    mfa_service: MFAService = Depends(get_mfa_service),
) -> SetupMFAUseCase:
    return SetupMFAUseCase(user_repository, mfa_service)


def get_enable_mfa_use_case(
    user_repository: UserRepository = Depends(get_user_repository),
    mfa_service: MFAService = Depends(get_mfa_service),
) -> EnableMFAUseCase:
    return EnableMFAUseCase(user_repository, mfa_service)


def get_list_sessions_use_case(
    session_repository: SessionRepository = Depends(get_session_repository),
) -> ListSessionsUseCase:
    return ListSessionsUseCase(session_repository)


def get_revoke_session_use_case(
    session_repository: SessionRepository = Depends(get_session_repository),
    refresh_token_repository: RefreshTokenRepository = Depends(
        get_refresh_token_repository
    ),
) -> RevokeSessionUseCase:
    return RevokeSessionUseCase(session_repository, refresh_token_repository)
