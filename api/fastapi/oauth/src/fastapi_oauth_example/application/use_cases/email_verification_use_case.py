import secrets

from fastapi_oauth_example.application.dto.user_dto import EmailVerificationDTO
from fastapi_oauth_example.application.services.email_service import EmailService
from fastapi_oauth_example.domain.repositories.user_repository import UserRepository
from fastapi_oauth_example.domain.value_objects.user_id import UserId


class SendEmailVerificationUseCase:
    def __init__(
        self,
        user_repository: UserRepository,
        email_service: EmailService,
        token_expire_hours: int = 24,
    ):
        self._user_repository = user_repository
        self._email_service = email_service
        self._token_expire_hours = token_expire_hours

    async def execute(self, user_id: UserId) -> None:
        user = await self._user_repository.get_by_id(user_id)

        if not user:
            raise ValueError("User not found")

        if user.is_verified:
            raise ValueError("User already verified")

        token = secrets.token_urlsafe(32)
        await self._email_service.send_verification_email(str(user.email), token)


class VerifyEmailUseCase:
    def __init__(self, user_repository: UserRepository):
        self._user_repository = user_repository

    async def execute(self, dto: EmailVerificationDTO) -> None:
        raise NotImplementedError(
            "Email verification use case requires token repository integration"
        )
