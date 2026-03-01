from datetime import timedelta

from fastapi_oauth_example.application.dto.user_dto import TokenDTO, UserLoginDTO
from fastapi_oauth_example.domain.repositories.user_repository import UserRepository
from fastapi_oauth_example.infrastructure.security.jwt_handler import JWTHandler
from fastapi_oauth_example.infrastructure.security.password_hasher import (
    PasswordHasher,
)


class LoginUserUseCase:
    def __init__(
        self,
        user_repository: UserRepository,
        password_hasher: PasswordHasher,
        jwt_handler: JWTHandler,
        access_token_expire_minutes: int = 30,
        refresh_token_expire_days: int = 7,
    ):
        self._user_repository = user_repository
        self._password_hasher = password_hasher
        self._jwt_handler = jwt_handler
        self._access_token_expire_minutes = access_token_expire_minutes
        self._refresh_token_expire_days = refresh_token_expire_days

    async def execute(self, dto: UserLoginDTO) -> TokenDTO:
        user = await self._user_repository.get_by_username(dto.username)

        if not user:
            raise ValueError("Invalid credentials")

        if not self._password_hasher.verify(dto.password, user.hashed_password):
            raise ValueError("Invalid credentials")

        if not user.is_active:
            raise ValueError("User is inactive")

        access_token_expires = timedelta(minutes=self._access_token_expire_minutes)
        access_token = self._jwt_handler.create_access_token(
            data={"sub": dto.username}, expires_delta=access_token_expires
        )

        refresh_token_expires = timedelta(days=self._refresh_token_expire_days)
        refresh_token = self._jwt_handler.create_refresh_token(
            data={"sub": dto.username}, expires_delta=refresh_token_expires
        )

        return TokenDTO(access_token=access_token, refresh_token=refresh_token)
