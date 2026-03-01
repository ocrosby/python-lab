from fastapi_oauth_example.application.dto.user_dto import UserResponseDTO
from fastapi_oauth_example.domain.repositories.user_repository import UserRepository
from fastapi_oauth_example.infrastructure.security.jwt_handler import JWTHandler


class VerifyTokenUseCase:
    def __init__(self, user_repository: UserRepository, jwt_handler: JWTHandler):
        self._user_repository = user_repository
        self._jwt_handler = jwt_handler

    async def execute(self, token: str) -> UserResponseDTO:
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
            created_at=user.created_at,
            updated_at=user.updated_at,
        )
