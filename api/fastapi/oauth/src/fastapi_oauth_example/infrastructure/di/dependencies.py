from collections.abc import AsyncGenerator

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi_oauth_example.application.use_cases.login_user_use_case import (
    LoginUserUseCase,
)
from fastapi_oauth_example.application.use_cases.register_user_use_case import (
    RegisterUserUseCase,
)
from fastapi_oauth_example.application.use_cases.verify_token_use_case import (
    VerifyTokenUseCase,
)
from fastapi_oauth_example.domain.repositories.user_repository import UserRepository
from fastapi_oauth_example.infrastructure.config.settings import settings
from fastapi_oauth_example.infrastructure.persistence.database import Database
from fastapi_oauth_example.infrastructure.persistence.postgres_user_repository import (
    PostgresUserRepository,
)
from fastapi_oauth_example.infrastructure.security.jwt_handler import JWTHandler
from fastapi_oauth_example.infrastructure.security.password_hasher import (
    PasswordHasher,
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

database = Database(settings.database_url)


async def get_db_session() -> AsyncGenerator[AsyncSession]:
    async for session in database.get_session():
        yield session


def get_password_hasher() -> PasswordHasher:
    return PasswordHasher()


def get_jwt_handler() -> JWTHandler:
    return JWTHandler(
        secret_key=settings.secret_key,
        algorithm=settings.algorithm,
        access_token_expire_minutes=settings.access_token_expire_minutes,
        refresh_token_expire_days=settings.refresh_token_expire_days,
    )


def get_user_repository(
    session: AsyncSession = Depends(get_db_session),
) -> UserRepository:
    return PostgresUserRepository(session)


def get_register_user_use_case(
    user_repository: UserRepository = Depends(get_user_repository),
    password_hasher: PasswordHasher = Depends(get_password_hasher),
) -> RegisterUserUseCase:
    return RegisterUserUseCase(user_repository, password_hasher)


def get_login_user_use_case(
    user_repository: UserRepository = Depends(get_user_repository),
    password_hasher: PasswordHasher = Depends(get_password_hasher),
    jwt_handler: JWTHandler = Depends(get_jwt_handler),
) -> LoginUserUseCase:
    return LoginUserUseCase(
        user_repository,
        password_hasher,
        jwt_handler,
        settings.access_token_expire_minutes,
    )


def get_verify_token_use_case(
    user_repository: UserRepository = Depends(get_user_repository),
    jwt_handler: JWTHandler = Depends(get_jwt_handler),
) -> VerifyTokenUseCase:
    return VerifyTokenUseCase(user_repository, jwt_handler)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    verify_token_use_case: VerifyTokenUseCase = Depends(get_verify_token_use_case),
):
    return await verify_token_use_case.execute(token)
