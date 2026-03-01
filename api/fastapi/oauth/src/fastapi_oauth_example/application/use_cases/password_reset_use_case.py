import secrets

from fastapi_oauth_example.application.dto.user_dto import (
    PasswordResetDTO,
    PasswordResetRequestDTO,
)
from fastapi_oauth_example.application.services.email_service import EmailService
from fastapi_oauth_example.domain.repositories.user_repository import UserRepository
from fastapi_oauth_example.domain.value_objects.email import Email
from fastapi_oauth_example.infrastructure.security.password_hasher import (
    PasswordHasher,
)


class RequestPasswordResetUseCase:
    def __init__(
        self,
        user_repository: UserRepository,
        email_service: EmailService,
        token_expire_hours: int = 1,
    ):
        self._user_repository = user_repository
        self._email_service = email_service
        self._token_expire_hours = token_expire_hours

    async def execute(self, dto: PasswordResetRequestDTO) -> None:
        user = await self._user_repository.get_by_email(Email(value=dto.email))

        if user:
            token = secrets.token_urlsafe(32)
            await self._email_service.send_password_reset_email(dto.email, token)


class ResetPasswordUseCase:
    def __init__(
        self,
        user_repository: UserRepository,
        password_hasher: PasswordHasher,
    ):
        self._user_repository = user_repository
        self._password_hasher = password_hasher

    async def execute(self, dto: PasswordResetDTO) -> None:
        raise NotImplementedError(
            "Password reset use case requires token repository integration"
        )
