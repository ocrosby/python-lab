"""Unit tests for TokenBlacklistService."""

from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock

import pytest

from fastapi_oauth_example.infrastructure.security.token_blacklist import (
    TokenBlacklistService,
)


def make_session():
    session = MagicMock()
    session.add = MagicMock()
    session.commit = AsyncMock()
    session.execute = AsyncMock()
    return session


@pytest.fixture
def svc():
    return TokenBlacklistService()


@pytest.mark.unit
class TestTokenBlacklistService:
    async def test_blacklist_token_adds_and_commits(self, svc):
        session = make_session()
        expires = datetime.utcnow() + timedelta(hours=1)
        await svc.blacklist_token(session, "tok", expires)
        session.add.assert_called_once()
        session.commit.assert_called_once()

    async def test_is_blacklisted_returns_true_when_found(self, svc):
        session = make_session()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = MagicMock()
        session.execute = AsyncMock(return_value=mock_result)
        result = await svc.is_blacklisted(session, "tok")
        assert result is True

    async def test_is_blacklisted_returns_false_when_not_found(self, svc):
        session = make_session()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        session.execute = AsyncMock(return_value=mock_result)
        result = await svc.is_blacklisted(session, "tok")
        assert result is False

    async def test_cleanup_expired_tokens_executes_and_commits(self, svc):
        session = make_session()
        await svc.cleanup_expired_tokens(session)
        session.execute.assert_called_once()
        session.commit.assert_called_once()
