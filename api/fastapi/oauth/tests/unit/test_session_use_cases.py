"""Unit tests for session use cases."""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from fastapi_oauth_example.application.dto.user_dto import SessionResponseDTO
from fastapi_oauth_example.application.use_cases.session_use_cases import (
    ListSessionsUseCase,
    RevokeSessionUseCase,
)
from fastapi_oauth_example.domain.value_objects.user_id import UserId


def make_session_model(session_id=None):
    now = datetime.utcnow()
    m = MagicMock()
    m.id = session_id or uuid4()
    m.ip_address = "127.0.0.1"
    m.user_agent = "TestAgent"
    m.last_accessed_at = now
    m.created_at = now
    m.refresh_token_id = uuid4()
    return m


@pytest.mark.unit
class TestListSessionsUseCase:
    async def test_returns_list_of_session_dtos(self):
        session_repo = MagicMock()
        session_repo.get_by_user_id = AsyncMock(
            return_value=[make_session_model(), make_session_model()]
        )
        uc = ListSessionsUseCase(session_repo)
        result = await uc.execute(UserId(value=uuid4()))
        assert len(result) == 2
        assert all(isinstance(s, SessionResponseDTO) for s in result)

    async def test_returns_empty_list_when_no_sessions(self):
        session_repo = MagicMock()
        session_repo.get_by_user_id = AsyncMock(return_value=[])
        uc = ListSessionsUseCase(session_repo)
        result = await uc.execute(UserId(value=uuid4()))
        assert result == []

    async def test_dto_fields_mapped_correctly(self):
        model = make_session_model()
        session_repo = MagicMock()
        session_repo.get_by_user_id = AsyncMock(return_value=[model])
        uc = ListSessionsUseCase(session_repo)
        result = await uc.execute(UserId(value=uuid4()))
        assert result[0].id == model.id
        assert result[0].ip_address == "127.0.0.1"


@pytest.mark.unit
class TestRevokeSessionUseCase:
    async def test_deletes_session_and_revokes_refresh_token(self):
        session_id = uuid4()
        model = make_session_model(session_id=session_id)
        session_repo = MagicMock()
        session_repo.get_by_user_id = AsyncMock(return_value=[model])
        session_repo.delete_by_id = AsyncMock(return_value=True)
        refresh_repo = MagicMock()
        refresh_repo.revoke_by_id = AsyncMock()

        uc = RevokeSessionUseCase(session_repo, refresh_repo)
        await uc.execute(UserId(value=uuid4()), session_id)

        session_repo.delete_by_id.assert_called_once_with(session_id)
        refresh_repo.revoke_by_id.assert_called_once_with(model.refresh_token_id)

    async def test_raises_when_session_not_found(self):
        session_repo = MagicMock()
        session_repo.get_by_user_id = AsyncMock(return_value=[])
        refresh_repo = MagicMock()

        uc = RevokeSessionUseCase(session_repo, refresh_repo)
        with pytest.raises(ValueError, match="Session not found"):
            await uc.execute(UserId(value=uuid4()), uuid4())

    async def test_raises_when_session_belongs_to_different_user(self):
        other_session = make_session_model()
        session_repo = MagicMock()
        session_repo.get_by_user_id = AsyncMock(return_value=[other_session])
        refresh_repo = MagicMock()

        uc = RevokeSessionUseCase(session_repo, refresh_repo)
        # Pass a session_id that doesn't match the user's sessions
        with pytest.raises(ValueError, match="Session not found"):
            await uc.execute(UserId(value=uuid4()), uuid4())
