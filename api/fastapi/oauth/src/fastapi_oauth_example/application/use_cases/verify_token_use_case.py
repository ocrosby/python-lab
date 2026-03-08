from sqlalchemy.ext.asyncio import AsyncSession

from fastapi_oauth_example.application.dto.user_dto import UserResponseDTO
from fastapi_oauth_example.infrastructure.security.jwt_handler import JWTHandler
from fastapi_oauth_example.infrastructure.security.token_blacklist import (
    TokenBlacklistService,
)
from fastapi_oauth_example.ports.outbound.user_repository import UserRepository


class VerifyTokenUseCase:
    def __init__(
        self,
        user_repository: UserRepository,
        jwt_handler: JWTHandler,
        token_blacklist: TokenBlacklistService,
        session: AsyncSession,
    ):
        self._user_repository = user_repository
        self._jwt_handler = jwt_handler
        self._token_blacklist = token_blacklist
        self._session = session

    async def execute(self, token: str) -> UserResponseDTO:
        if await self._token_blacklist.is_blacklisted(self._session, token):
            raise ValueError("Token has been revoked")

        payload = self._jwt_handler.decode_token(token)

        if not payload:
            raise ValueError("Invalid token")

        username: str = payload.get("sub")
        if not username:
            raise ValueError("Invalid token payload")

        user = await self._user_repository.get_by_username(username)

        if not user:
            raise ValueError("User not found")

        return UserResponseDTO(
            id=user.id.value,
            email=str(user.email),
            username=user.username,
            is_active=user.is_active,
            is_verified=user.is_verified,
            mfa_enabled=user.mfa_enabled,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )
