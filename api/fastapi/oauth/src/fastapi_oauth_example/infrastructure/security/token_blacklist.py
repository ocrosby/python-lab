from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi_oauth_example.infrastructure.persistence.models import TokenBlacklistModel


class TokenBlacklistService:
    async def blacklist_token(
        self, session: AsyncSession, token: str, expires_at: datetime
    ) -> None:
        blacklist_entry = TokenBlacklistModel(token=token, expires_at=expires_at)
        session.add(blacklist_entry)
        await session.commit()

    async def is_blacklisted(self, session: AsyncSession, token: str) -> bool:
        result = await session.execute(
            select(TokenBlacklistModel).where(TokenBlacklistModel.token == token)
        )
        return result.scalar_one_or_none() is not None

    async def cleanup_expired_tokens(self, session: AsyncSession) -> None:
        await session.execute(
            select(TokenBlacklistModel).where(
                TokenBlacklistModel.expires_at < datetime.utcnow()
            )
        )
        await session.commit()
