from datetime import timedelta

from fastapi_oauth_example.application.dto.user_dto import RefreshTokenDTO, TokenDTO
from fastapi_oauth_example.domain.repositories.user_repository import UserRepository
from fastapi_oauth_example.infrastructure.security.jwt_handler import JWTHandler


class RefreshTokenUseCase:
    def __init__(
        self,
        user_repository: UserRepository,
        jwt_handler: JWTHandler,
        access_token_expire_minutes: int = 30,
    ):
        self._user_repository = user_repository
        self._jwt_handler = jwt_handler
        self._access_token_expire_minutes = access_token_expire_minutes

    async def execute(self, dto: RefreshTokenDTO) -> TokenDTO:
        payload = self._jwt_handler.decode_token(dto.refresh_token)

        if not payload or payload.get("type") != "refresh":
            raise ValueError("Invalid refresh token")

        username = payload.get("sub")
        if not username:
            raise ValueError("Invalid refresh token")

        user = await self._user_repository.get_by_username(username)
        if not user or not user.is_active:
            raise ValueError("Invalid user")

        access_token_expires = timedelta(minutes=self._access_token_expire_minutes)
        access_token = self._jwt_handler.create_access_token(
            data={"sub": username}, expires_delta=access_token_expires
        )

        return TokenDTO(
            access_token=access_token,
            refresh_token=dto.refresh_token,
        )
