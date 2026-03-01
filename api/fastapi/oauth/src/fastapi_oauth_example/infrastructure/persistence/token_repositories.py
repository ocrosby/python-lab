from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi_oauth_example.infrastructure.persistence.models import (
    EmailVerificationTokenModel,
    PasswordResetTokenModel,
    RefreshTokenModel,
    SessionModel,
)


class RefreshTokenRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(
        self, user_id: UUID, token: str, expires_at: datetime
    ) -> RefreshTokenModel:
        refresh_token = RefreshTokenModel(
            user_id=user_id, token=token, expires_at=expires_at
        )
        self._session.add(refresh_token)
        await self._session.commit()
        await self._session.refresh(refresh_token)
        return refresh_token

    async def get_by_token(self, token: str) -> RefreshTokenModel | None:
        result = await self._session.execute(
            select(RefreshTokenModel).where(RefreshTokenModel.token == token)
        )
        return result.scalar_one_or_none()

    async def revoke(self, token: str) -> None:
        result = await self._session.execute(
            select(RefreshTokenModel).where(RefreshTokenModel.token == token)
        )
        refresh_token = result.scalar_one_or_none()
        if refresh_token:
            refresh_token.revoked = True
            await self._session.commit()


class PasswordResetTokenRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(
        self, user_id: UUID, token: str, expires_at: datetime
    ) -> PasswordResetTokenModel:
        reset_token = PasswordResetTokenModel(
            user_id=user_id, token=token, expires_at=expires_at
        )
        self._session.add(reset_token)
        await self._session.commit()
        await self._session.refresh(reset_token)
        return reset_token

    async def get_by_token(self, token: str) -> PasswordResetTokenModel | None:
        result = await self._session.execute(
            select(PasswordResetTokenModel).where(
                PasswordResetTokenModel.token == token
            )
        )
        return result.scalar_one_or_none()

    async def mark_as_used(self, token: str) -> None:
        result = await self._session.execute(
            select(PasswordResetTokenModel).where(
                PasswordResetTokenModel.token == token
            )
        )
        reset_token = result.scalar_one_or_none()
        if reset_token:
            reset_token.used = True
            await self._session.commit()


class EmailVerificationTokenRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(
        self, user_id: UUID, token: str, expires_at: datetime
    ) -> EmailVerificationTokenModel:
        verification_token = EmailVerificationTokenModel(
            user_id=user_id, token=token, expires_at=expires_at
        )
        self._session.add(verification_token)
        await self._session.commit()
        await self._session.refresh(verification_token)
        return verification_token

    async def get_by_token(self, token: str) -> EmailVerificationTokenModel | None:
        result = await self._session.execute(
            select(EmailVerificationTokenModel).where(
                EmailVerificationTokenModel.token == token
            )
        )
        return result.scalar_one_or_none()

    async def mark_as_used(self, token: str) -> None:
        result = await self._session.execute(
            select(EmailVerificationTokenModel).where(
                EmailVerificationTokenModel.token == token
            )
        )
        verification_token = result.scalar_one_or_none()
        if verification_token:
            verification_token.used = True
            await self._session.commit()


class SessionRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(
        self,
        user_id: UUID,
        refresh_token_id: UUID,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> SessionModel:
        session_model = SessionModel(
            user_id=user_id,
            refresh_token_id=refresh_token_id,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        self._session.add(session_model)
        await self._session.commit()
        await self._session.refresh(session_model)
        return session_model

    async def get_by_user_id(self, user_id: UUID) -> list[SessionModel]:
        result = await self._session.execute(
            select(SessionModel).where(SessionModel.user_id == user_id)
        )
        return list(result.scalars().all())

    async def delete_by_id(self, session_id: UUID) -> bool:
        result = await self._session.execute(
            select(SessionModel).where(SessionModel.id == session_id)
        )
        session_model = result.scalar_one_or_none()
        if session_model:
            await self._session.delete(session_model)
            await self._session.commit()
            return True
        return False
