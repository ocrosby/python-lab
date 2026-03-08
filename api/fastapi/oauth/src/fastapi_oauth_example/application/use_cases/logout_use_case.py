from datetime import datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from fastapi_oauth_example.adapters.outbound.persistence.token_repositories import (
    RefreshTokenRepository,
)
from fastapi_oauth_example.infrastructure.security.audit_logger import AuditLogger
from fastapi_oauth_example.infrastructure.security.jwt_handler import JWTHandler
from fastapi_oauth_example.infrastructure.security.token_blacklist import (
    TokenBlacklistService,
)


class LogoutUseCase:
    def __init__(
        self,
        token_blacklist: TokenBlacklistService,
        refresh_token_repo: RefreshTokenRepository,
        jwt_handler: JWTHandler,
        audit_logger: AuditLogger,
        db_session: AsyncSession,
    ):
        self._token_blacklist = token_blacklist
        self._refresh_repo = refresh_token_repo
        self._jwt_handler = jwt_handler
        self._audit_logger = audit_logger
        self._db_session = db_session

    async def execute(
        self,
        access_token: str,
        user_id: UUID,
        refresh_token: str | None = None,
        ip_address: str | None = None,
    ) -> None:
        await self._blacklist_access_token(access_token)
        if refresh_token:
            await self._refresh_repo.revoke(refresh_token)
        await self._audit_logger.log_event(
            self._db_session, "logout", user_id, ip_address
        )

    async def _blacklist_access_token(self, access_token: str) -> None:
        payload = self._jwt_handler.decode_token(access_token)
        exp = payload.get("exp") if payload else None
        expires_at = datetime.utcfromtimestamp(exp) if exp else datetime.utcnow()
        await self._token_blacklist.blacklist_token(
            self._db_session, access_token, expires_at
        )
