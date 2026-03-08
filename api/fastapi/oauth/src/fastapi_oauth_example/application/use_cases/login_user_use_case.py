from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from fastapi_oauth_example.adapters.outbound.persistence.token_repositories import (
    RefreshTokenRepository,
    SessionRepository,
)
from fastapi_oauth_example.application.dto.user_dto import TokenDTO, UserLoginDTO
from fastapi_oauth_example.domain.entities.user import User
from fastapi_oauth_example.infrastructure.security.account_lockout import (
    AccountLockoutService,
)
from fastapi_oauth_example.infrastructure.security.audit_logger import AuditLogger
from fastapi_oauth_example.infrastructure.security.jwt_handler import JWTHandler
from fastapi_oauth_example.infrastructure.security.mfa_service import MFAService
from fastapi_oauth_example.infrastructure.security.password_hasher import PasswordHasher
from fastapi_oauth_example.ports.outbound.user_repository import UserRepository


class LoginUserUseCase:
    def __init__(
        self,
        user_repository: UserRepository,
        password_hasher: PasswordHasher,
        jwt_handler: JWTHandler,
        lockout_service: AccountLockoutService,
        mfa_service: MFAService,
        refresh_repo: RefreshTokenRepository,
        session_repo: SessionRepository,
        audit_logger: AuditLogger,
        db_session: AsyncSession,
        access_token_expire_minutes: int = 30,
        refresh_token_expire_days: int = 7,
    ):
        self._user_repository = user_repository
        self._password_hasher = password_hasher
        self._jwt_handler = jwt_handler
        self._lockout_service = lockout_service
        self._mfa_service = mfa_service
        self._refresh_repo = refresh_repo
        self._session_repo = session_repo
        self._audit_logger = audit_logger
        self._db_session = db_session
        self._access_token_expire_minutes = access_token_expire_minutes
        self._refresh_token_expire_days = refresh_token_expire_days

    async def execute(
        self,
        dto: UserLoginDTO,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> TokenDTO:
        user = await self._get_validated_user(dto)
        await self._handle_mfa(user, dto)
        await self._lockout_service.reset_failed_attempts(user, self._user_repository)
        return await self._create_tokens_and_session(user, ip_address, user_agent)

    async def _get_validated_user(self, dto: UserLoginDTO) -> User:
        user = await self._user_repository.get_by_username(dto.username)
        if not user:
            raise ValueError("Invalid credentials")
        if self._lockout_service.is_locked(user):
            raise ValueError("Account is locked")
        await self._verify_password(user, dto.password)
        if not user.is_active:
            raise ValueError("Inactive account")
        return user

    async def _verify_password(self, user: User, password: str) -> None:
        if not self._password_hasher.verify(password, user.hashed_password):
            await self._lockout_service.record_failed_attempt(
                user, self._user_repository
            )
            raise ValueError("Invalid credentials")

    async def _handle_mfa(self, user: User, dto: UserLoginDTO) -> None:
        if not user.mfa_enabled:
            return
        if dto.mfa_code is None:
            raise ValueError("MFA code required")
        if not self._mfa_service.verify_code(user.mfa_secret, dto.mfa_code):
            await self._lockout_service.record_failed_attempt(
                user, self._user_repository
            )
            raise ValueError("Invalid MFA code")

    async def _create_tokens_and_session(
        self,
        user: User,
        ip_address: str | None,
        user_agent: str | None,
    ) -> TokenDTO:
        access_token = self._jwt_handler.create_access_token(
            data={"sub": user.username}
        )
        refresh_token_str = self._jwt_handler.create_refresh_token(
            data={"sub": user.username}
        )
        expires_at = datetime.utcnow() + timedelta(days=self._refresh_token_expire_days)
        rt = await self._refresh_repo.create(
            user.id.value, refresh_token_str, expires_at
        )
        await self._session_repo.create(user.id.value, rt.id, ip_address, user_agent)
        await self._audit_logger.log_event(
            self._db_session, "login_success", user.id.value, ip_address, user_agent
        )
        return TokenDTO(access_token=access_token, refresh_token=refresh_token_str)
