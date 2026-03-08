"""Unit tests for token repositories."""

from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from fastapi_oauth_example.adapters.outbound.persistence.token_repositories import (
    EmailVerificationTokenRepository,
    PasswordResetTokenRepository,
    RefreshTokenRepository,
    SessionRepository,
)


def make_session(model=None):
    session = AsyncMock()
    result = MagicMock()
    result.scalar_one_or_none.return_value = model
    session.execute.return_value = result
    return session


def make_rt(revoked=False):
    m = MagicMock()
    m.id = uuid4()
    m.token = "tok"
    m.revoked = revoked
    return m


def make_prt(used=False):
    m = MagicMock()
    m.id = uuid4()
    m.token = "tok"
    m.used = used
    return m


def make_evt(used=False):
    m = MagicMock()
    m.id = uuid4()
    m.token = "tok"
    m.used = used
    return m


def make_session_model():
    m = MagicMock()
    m.id = uuid4()
    m.user_id = uuid4()
    m.refresh_token_id = uuid4()
    m.ip_address = "1.2.3.4"
    m.user_agent = "pytest"
    return m


@pytest.mark.unit
class TestRefreshTokenRepository:
    async def test_create_returns_model(self):
        session = make_session()
        repo = RefreshTokenRepository(session)
        result = await repo.create(
            uuid4(), "tok", datetime.utcnow() + timedelta(days=7)
        )
        assert result is not None
        session.add.assert_called_once()
        session.commit.assert_called_once()

    async def test_get_by_token_returns_model(self):
        model = make_rt()
        session = make_session(model)
        repo = RefreshTokenRepository(session)
        result = await repo.get_by_token("tok")
        assert result is model

    async def test_get_by_token_returns_none_when_not_found(self):
        session = make_session(None)
        repo = RefreshTokenRepository(session)
        result = await repo.get_by_token("missing")
        assert result is None

    async def test_revoke_sets_revoked_flag(self):
        model = make_rt()
        session = make_session(model)
        repo = RefreshTokenRepository(session)
        await repo.revoke("tok")
        assert model.revoked is True
        session.commit.assert_called_once()

    async def test_revoke_noop_when_not_found(self):
        session = make_session(None)
        repo = RefreshTokenRepository(session)
        await repo.revoke("missing")
        session.commit.assert_not_called()

    async def test_revoke_by_id_sets_revoked_flag(self):
        model = make_rt()
        session = make_session(model)
        repo = RefreshTokenRepository(session)
        await repo.revoke_by_id(uuid4())
        assert model.revoked is True
        session.commit.assert_called_once()

    async def test_revoke_by_id_noop_when_not_found(self):
        session = make_session(None)
        repo = RefreshTokenRepository(session)
        await repo.revoke_by_id(uuid4())
        session.commit.assert_not_called()


@pytest.mark.unit
class TestPasswordResetTokenRepository:
    async def test_create_returns_model(self):
        session = make_session()
        repo = PasswordResetTokenRepository(session)
        result = await repo.create(
            uuid4(), "tok", datetime.utcnow() + timedelta(hours=1)
        )
        assert result is not None
        session.add.assert_called_once()

    async def test_get_by_token_returns_model(self):
        model = make_prt()
        session = make_session(model)
        repo = PasswordResetTokenRepository(session)
        result = await repo.get_by_token("tok")
        assert result is model

    async def test_get_by_token_returns_none_when_not_found(self):
        session = make_session(None)
        repo = PasswordResetTokenRepository(session)
        result = await repo.get_by_token("missing")
        assert result is None

    async def test_mark_as_used_sets_used_flag(self):
        model = make_prt()
        session = make_session(model)
        repo = PasswordResetTokenRepository(session)
        await repo.mark_as_used("tok")
        assert model.used is True
        session.commit.assert_called_once()

    async def test_mark_as_used_noop_when_not_found(self):
        session = make_session(None)
        repo = PasswordResetTokenRepository(session)
        await repo.mark_as_used("missing")
        session.commit.assert_not_called()


@pytest.mark.unit
class TestEmailVerificationTokenRepository:
    async def test_create_returns_model(self):
        session = make_session()
        repo = EmailVerificationTokenRepository(session)
        result = await repo.create(
            uuid4(), "tok", datetime.utcnow() + timedelta(hours=24)
        )
        assert result is not None
        session.add.assert_called_once()

    async def test_get_by_token_returns_model(self):
        model = make_evt()
        session = make_session(model)
        repo = EmailVerificationTokenRepository(session)
        result = await repo.get_by_token("tok")
        assert result is model

    async def test_get_by_token_returns_none_when_not_found(self):
        session = make_session(None)
        repo = EmailVerificationTokenRepository(session)
        result = await repo.get_by_token("missing")
        assert result is None

    async def test_mark_as_used_sets_used_flag(self):
        model = make_evt()
        session = make_session(model)
        repo = EmailVerificationTokenRepository(session)
        await repo.mark_as_used("tok")
        assert model.used is True
        session.commit.assert_called_once()

    async def test_mark_as_used_noop_when_not_found(self):
        session = make_session(None)
        repo = EmailVerificationTokenRepository(session)
        await repo.mark_as_used("missing")
        session.commit.assert_not_called()


@pytest.mark.unit
class TestSessionRepository:
    async def test_create_returns_session_model(self):
        session = make_session()
        repo = SessionRepository(session)
        result = await repo.create(uuid4(), uuid4(), "1.2.3.4", "pytest")
        assert result is not None
        session.add.assert_called_once()

    async def test_get_by_user_id_returns_list(self):
        models = [make_session_model(), make_session_model()]
        session = AsyncMock()
        result_mock = MagicMock()
        result_mock.scalars.return_value.all.return_value = models
        session.execute.return_value = result_mock
        repo = SessionRepository(session)
        result = await repo.get_by_user_id(uuid4())
        assert len(result) == 2

    async def test_delete_by_id_returns_true_when_found(self):
        model = make_session_model()
        session = make_session(model)
        repo = SessionRepository(session)
        result = await repo.delete_by_id(uuid4())
        assert result is True
        session.delete.assert_called_once_with(model)

    async def test_delete_by_id_returns_false_when_not_found(self):
        session = make_session(None)
        repo = SessionRepository(session)
        result = await repo.delete_by_id(uuid4())
        assert result is False
