from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi_oauth_example.domain.entities.user import User
from fastapi_oauth_example.domain.repositories.user_repository import UserRepository
from fastapi_oauth_example.domain.value_objects.email import Email
from fastapi_oauth_example.domain.value_objects.user_id import UserId
from fastapi_oauth_example.infrastructure.persistence.models import UserModel


class PostgresUserRepository(UserRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, user: User) -> User:
        user_model = UserModel(
            id=user.id.value,
            email=str(user.email),
            username=user.username,
            hashed_password=user.hashed_password,
            is_active=user.is_active,
            is_verified=user.is_verified,
            email_verified_at=user.email_verified_at,
            failed_login_attempts=user.failed_login_attempts,
            locked_until=user.locked_until,
            mfa_enabled=user.mfa_enabled,
            mfa_secret=user.mfa_secret,
            created_at=user.created_at or datetime.utcnow(),
            updated_at=user.updated_at or datetime.utcnow(),
        )
        self._session.add(user_model)
        await self._session.commit()
        await self._session.refresh(user_model)
        return self._model_to_entity(user_model)

    async def get_by_id(self, user_id: UserId) -> User | None:
        stmt = select(UserModel).where(UserModel.id == user_id.value)
        result = await self._session.execute(stmt)
        user_model = result.scalar_one_or_none()
        return self._model_to_entity(user_model) if user_model else None

    async def get_by_email(self, email: Email) -> User | None:
        stmt = select(UserModel).where(UserModel.email == str(email))
        result = await self._session.execute(stmt)
        user_model = result.scalar_one_or_none()
        return self._model_to_entity(user_model) if user_model else None

    async def get_by_username(self, username: str) -> User | None:
        stmt = select(UserModel).where(UserModel.username == username)
        result = await self._session.execute(stmt)
        user_model = result.scalar_one_or_none()
        return self._model_to_entity(user_model) if user_model else None

    async def update(self, user: User) -> User:
        stmt = select(UserModel).where(UserModel.id == user.id.value)
        result = await self._session.execute(stmt)
        user_model = result.scalar_one()

        user_model.email = str(user.email)
        user_model.username = user.username
        user_model.hashed_password = user.hashed_password
        user_model.is_active = user.is_active
        user_model.is_verified = user.is_verified
        user_model.email_verified_at = user.email_verified_at
        user_model.failed_login_attempts = user.failed_login_attempts
        user_model.locked_until = user.locked_until
        user_model.mfa_enabled = user.mfa_enabled
        user_model.mfa_secret = user.mfa_secret
        user_model.updated_at = datetime.utcnow()

        await self._session.commit()
        await self._session.refresh(user_model)
        return self._model_to_entity(user_model)

    async def delete(self, user_id: UserId) -> bool:
        stmt = select(UserModel).where(UserModel.id == user_id.value)
        result = await self._session.execute(stmt)
        user_model = result.scalar_one_or_none()

        if user_model:
            await self._session.delete(user_model)
            await self._session.commit()
            return True
        return False

    async def exists_by_email(self, email: Email) -> bool:
        stmt = select(UserModel).where(UserModel.email == str(email))
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def exists_by_username(self, username: str) -> bool:
        stmt = select(UserModel).where(UserModel.username == username)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none() is not None

    @staticmethod
    def _model_to_entity(model: UserModel) -> User:
        return User(
            id=UserId(value=model.id),
            email=Email(value=model.email),
            username=model.username,
            hashed_password=model.hashed_password,
            is_active=model.is_active,
            is_verified=model.is_verified,
            email_verified_at=model.email_verified_at,
            failed_login_attempts=model.failed_login_attempts,
            locked_until=model.locked_until,
            mfa_enabled=model.mfa_enabled,
            mfa_secret=model.mfa_secret,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
