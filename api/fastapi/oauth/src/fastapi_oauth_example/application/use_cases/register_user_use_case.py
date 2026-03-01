from uuid import uuid4

from fastapi_oauth_example.application.dto.user_dto import (
    UserRegistrationDTO,
    UserResponseDTO,
)
from fastapi_oauth_example.domain.entities.user import User
from fastapi_oauth_example.domain.repositories.user_repository import UserRepository
from fastapi_oauth_example.domain.value_objects.email import Email
from fastapi_oauth_example.domain.value_objects.user_id import UserId
from fastapi_oauth_example.infrastructure.security.password_hasher import (
    PasswordHasher,
)


class RegisterUserUseCase:
    def __init__(
        self, user_repository: UserRepository, password_hasher: PasswordHasher
    ):
        self._user_repository = user_repository
        self._password_hasher = password_hasher

    async def execute(self, dto: UserRegistrationDTO) -> UserResponseDTO:
        email = Email(value=dto.email)

        if await self._user_repository.exists_by_email(email):
            raise ValueError("Email already registered")

        if await self._user_repository.exists_by_username(dto.username):
            raise ValueError("Username already taken")

        hashed_password = self._password_hasher.hash(dto.password)

        user = User(
            id=UserId(value=uuid4()),
            email=email,
            username=dto.username,
            hashed_password=hashed_password,
        )

        created_user = await self._user_repository.create(user)

        return UserResponseDTO(
            id=created_user.id.value,
            email=str(created_user.email),
            username=created_user.username,
            is_active=created_user.is_active,
            is_verified=created_user.is_verified,
            created_at=created_user.created_at,
            updated_at=created_user.updated_at,
        )
