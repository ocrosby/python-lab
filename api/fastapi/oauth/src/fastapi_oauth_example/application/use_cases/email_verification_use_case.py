import secrets
from datetime import datetime, timedelta

from fastapi_oauth_example.adapters.outbound.persistence.models import (
    EmailVerificationTokenModel,
)
from fastapi_oauth_example.adapters.outbound.persistence.token_repositories import (
    EmailVerificationTokenRepository,
)
from fastapi_oauth_example.application.dto.user_dto import EmailVerificationDTO
from fastapi_oauth_example.application.services.email_service import EmailService
from fastapi_oauth_example.domain.value_objects.user_id import UserId
from fastapi_oauth_example.ports.outbound.user_repository import UserRepository


class SendEmailVerificationUseCase:
    def __init__(
        self,
        user_repository: UserRepository,
        email_service: EmailService,
        token_repository: EmailVerificationTokenRepository,
        token_expire_hours: int = 24,
    ):
        self._user_repository = user_repository
        self._email_service = email_service
        self._token_repository = token_repository
        self._token_expire_hours = token_expire_hours

    async def execute(self, user_id: UserId) -> None:
        user = await self._user_repository.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        if user.is_verified:
            raise ValueError("User already verified")
        token = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(hours=self._token_expire_hours)
        await self._token_repository.create(user.id.value, token, expires_at)
        await self._email_service.send_verification_email(str(user.email), token)


class VerifyEmailUseCase:
    def __init__(
        self,
        user_repository: UserRepository,
        token_repository: EmailVerificationTokenRepository,
    ):
        self._user_repository = user_repository
        self._token_repository = token_repository

    async def execute(self, dto: EmailVerificationDTO) -> None:
        token_model = await self._token_repository.get_by_token(dto.token)
        self._validate_token(token_model)
        user = await self._user_repository.get_by_id(UserId(value=token_model.user_id))
        if not user:
            raise ValueError("User not found")
        user.is_verified = True
        user.email_verified_at = datetime.utcnow()
        await self._user_repository.update(user)
        await self._token_repository.mark_as_used(dto.token)

    @staticmethod
    def _validate_token(token_model: EmailVerificationTokenModel | None) -> None:
        if not token_model:
            raise ValueError("Invalid or expired token")
        if token_model.used:
            raise ValueError("Token already used")
        if token_model.expires_at < datetime.utcnow():
            raise ValueError("Token has expired")
