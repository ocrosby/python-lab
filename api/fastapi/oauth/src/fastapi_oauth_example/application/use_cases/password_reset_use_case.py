import secrets
from datetime import datetime, timedelta

from fastapi_oauth_example.adapters.outbound.persistence.models import (
    PasswordResetTokenModel,
)
from fastapi_oauth_example.adapters.outbound.persistence.token_repositories import (
    PasswordResetTokenRepository,
)
from fastapi_oauth_example.application.dto.user_dto import (
    PasswordResetDTO,
    PasswordResetRequestDTO,
)
from fastapi_oauth_example.application.services.email_service import EmailService
from fastapi_oauth_example.domain.value_objects.email import Email
from fastapi_oauth_example.domain.value_objects.user_id import UserId
from fastapi_oauth_example.infrastructure.security.password_hasher import PasswordHasher
from fastapi_oauth_example.ports.outbound.user_repository import UserRepository


class RequestPasswordResetUseCase:
    def __init__(
        self,
        user_repository: UserRepository,
        email_service: EmailService,
        token_repository: PasswordResetTokenRepository,
        token_expire_hours: int = 1,
    ):
        self._user_repository = user_repository
        self._email_service = email_service
        self._token_repository = token_repository
        self._token_expire_hours = token_expire_hours

    async def execute(self, dto: PasswordResetRequestDTO) -> None:
        user = await self._user_repository.get_by_email(Email(value=dto.email))
        if user:
            token = secrets.token_urlsafe(32)
            expires_at = datetime.utcnow() + timedelta(hours=self._token_expire_hours)
            await self._token_repository.create(user.id.value, token, expires_at)
            await self._email_service.send_password_reset_email(dto.email, token)


class ResetPasswordUseCase:
    def __init__(
        self,
        user_repository: UserRepository,
        password_hasher: PasswordHasher,
        token_repository: PasswordResetTokenRepository,
    ):
        self._user_repository = user_repository
        self._password_hasher = password_hasher
        self._token_repository = token_repository

    async def execute(self, dto: PasswordResetDTO) -> None:
        token_model = await self._token_repository.get_by_token(dto.token)
        self._validate_token(token_model)
        user = await self._user_repository.get_by_id(UserId(value=token_model.user_id))
        if not user:
            raise ValueError("User not found")
        user.hashed_password = self._password_hasher.hash(dto.new_password)
        await self._user_repository.update(user)
        await self._token_repository.mark_as_used(dto.token)

    @staticmethod
    def _validate_token(token_model: PasswordResetTokenModel | None) -> None:
        if not token_model:
            raise ValueError("Invalid or expired token")
        if token_model.used:
            raise ValueError("Token already used")
        if token_model.expires_at < datetime.utcnow():
            raise ValueError("Token has expired")
