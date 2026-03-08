from fastapi_oauth_example.application.dto.user_dto import (
    MFASetupResponseDTO,
    MFAVerifyDTO,
)
from fastapi_oauth_example.domain.value_objects.user_id import UserId
from fastapi_oauth_example.infrastructure.security.mfa_service import MFAService
from fastapi_oauth_example.ports.outbound.user_repository import UserRepository


class SetupMFAUseCase:
    def __init__(self, user_repository: UserRepository, mfa_service: MFAService):
        self._user_repository = user_repository
        self._mfa_service = mfa_service

    async def execute(self, user_id: UserId) -> MFASetupResponseDTO:
        user = await self._user_repository.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        secret = self._mfa_service.generate_secret()
        qr_code_url = self._mfa_service.generate_qr_code(user.username, secret)
        user.mfa_secret = secret
        await self._user_repository.update(user)
        return MFASetupResponseDTO(secret=secret, qr_code_url=qr_code_url)


class EnableMFAUseCase:
    def __init__(self, user_repository: UserRepository, mfa_service: MFAService):
        self._user_repository = user_repository
        self._mfa_service = mfa_service

    async def execute(self, user_id: UserId, dto: MFAVerifyDTO) -> None:
        user = await self._user_repository.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        if not user.mfa_secret:
            raise ValueError("MFA not set up")
        if not self._mfa_service.verify_code(user.mfa_secret, dto.code):
            raise ValueError("Invalid MFA code")
        user.mfa_enabled = True
        await self._user_repository.update(user)
