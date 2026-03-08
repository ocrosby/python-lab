"""Unit tests for PostgresUserRepository."""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from fastapi_oauth_example.adapters.outbound.persistence.postgres_user_repository import (  # noqa: E501
    PostgresUserRepository,
)
from fastapi_oauth_example.domain.entities.user import User
from fastapi_oauth_example.domain.value_objects.email import Email
from fastapi_oauth_example.domain.value_objects.user_id import UserId


def make_user_model(**kwargs):
    m = MagicMock()
    m.id = uuid4()
    m.email = "u@example.com"
    m.username = "alice"
    m.hashed_password = "hashed"
    m.is_active = True
    m.is_verified = False
    m.email_verified_at = None
    m.failed_login_attempts = 0
    m.locked_until = None
    m.mfa_enabled = False
    m.mfa_secret = None
    m.created_at = datetime.utcnow()
    m.updated_at = datetime.utcnow()
    for k, v in kwargs.items():
        setattr(m, k, v)
    return m


def make_user():
    now = datetime.utcnow()
    return User(
        id=UserId(value=uuid4()),
        email=Email(value="u@example.com"),
        username="alice",
        hashed_password="hashed",
        created_at=now,
        updated_at=now,
    )


def make_session(model=None):
    session = AsyncMock()
    result = MagicMock()
    result.scalar_one_or_none.return_value = model
    result.scalar_one.return_value = model
    session.execute.return_value = result
    return session


@pytest.mark.unit
class TestPostgresUserRepository:
    async def test_create_returns_user(self):
        model = make_user_model()
        session = make_session(model)
        repo = PostgresUserRepository(session)
        result = await repo.create(make_user())
        assert result.username == model.username
        session.add.assert_called_once()
        session.commit.assert_called_once()

    async def test_get_by_id_returns_user(self):
        model = make_user_model()
        session = make_session(model)
        repo = PostgresUserRepository(session)
        result = await repo.get_by_id(UserId(value=uuid4()))
        assert result is not None
        assert result.username == model.username

    async def test_get_by_id_returns_none_when_not_found(self):
        session = make_session(None)
        repo = PostgresUserRepository(session)
        result = await repo.get_by_id(UserId(value=uuid4()))
        assert result is None

    async def test_get_by_email_returns_user(self):
        model = make_user_model()
        session = make_session(model)
        repo = PostgresUserRepository(session)
        result = await repo.get_by_email(Email(value="u@example.com"))
        assert result is not None

    async def test_get_by_email_returns_none_when_not_found(self):
        session = make_session(None)
        repo = PostgresUserRepository(session)
        result = await repo.get_by_email(Email(value="x@example.com"))
        assert result is None

    async def test_get_by_username_returns_user(self):
        model = make_user_model()
        session = make_session(model)
        repo = PostgresUserRepository(session)
        result = await repo.get_by_username("alice")
        assert result is not None

    async def test_get_by_username_returns_none_when_not_found(self):
        session = make_session(None)
        repo = PostgresUserRepository(session)
        result = await repo.get_by_username("nobody")
        assert result is None

    async def test_update_returns_updated_user(self):
        model = make_user_model()
        session = make_session(model)
        repo = PostgresUserRepository(session)
        result = await repo.update(make_user())
        assert result is not None
        session.commit.assert_called_once()

    async def test_delete_returns_true_when_found(self):
        model = make_user_model()
        session = make_session(model)
        repo = PostgresUserRepository(session)
        result = await repo.delete(UserId(value=uuid4()))
        assert result is True
        session.delete.assert_called_once_with(model)

    async def test_delete_returns_false_when_not_found(self):
        session = make_session(None)
        repo = PostgresUserRepository(session)
        result = await repo.delete(UserId(value=uuid4()))
        assert result is False

    async def test_exists_by_email_returns_true(self):
        session = make_session(make_user_model())
        repo = PostgresUserRepository(session)
        result = await repo.exists_by_email(Email(value="u@example.com"))
        assert result is True

    async def test_exists_by_email_returns_false(self):
        session = make_session(None)
        repo = PostgresUserRepository(session)
        result = await repo.exists_by_email(Email(value="x@example.com"))
        assert result is False

    async def test_exists_by_username_returns_true(self):
        session = make_session(make_user_model())
        repo = PostgresUserRepository(session)
        result = await repo.exists_by_username("alice")
        assert result is True

    async def test_exists_by_username_returns_false(self):
        session = make_session(None)
        repo = PostgresUserRepository(session)
        result = await repo.exists_by_username("nobody")
        assert result is False
