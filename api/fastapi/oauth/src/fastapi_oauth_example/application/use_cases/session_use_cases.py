from uuid import UUID

from fastapi_oauth_example.adapters.outbound.persistence.token_repositories import (
    RefreshTokenRepository,
    SessionRepository,
)
from fastapi_oauth_example.application.dto.user_dto import SessionResponseDTO
from fastapi_oauth_example.domain.value_objects.user_id import UserId


class ListSessionsUseCase:
    def __init__(self, session_repository: SessionRepository):
        self._session_repo = session_repository

    async def execute(self, user_id: UserId) -> list[SessionResponseDTO]:
        sessions = await self._session_repo.get_by_user_id(user_id.value)
        return [
            SessionResponseDTO(
                id=s.id,
                ip_address=s.ip_address,
                user_agent=s.user_agent,
                last_accessed_at=s.last_accessed_at,
                created_at=s.created_at,
            )
            for s in sessions
        ]


class RevokeSessionUseCase:
    def __init__(
        self,
        session_repository: SessionRepository,
        refresh_token_repository: RefreshTokenRepository,
    ):
        self._session_repo = session_repository
        self._refresh_repo = refresh_token_repository

    async def execute(self, user_id: UserId, session_id: UUID) -> None:
        sessions = await self._session_repo.get_by_user_id(user_id.value)
        target = next((s for s in sessions if s.id == session_id), None)
        if not target:
            raise ValueError("Session not found")
        refresh_token_id = target.refresh_token_id
        await self._session_repo.delete_by_id(session_id)
        await self._refresh_repo.revoke_by_id(refresh_token_id)
