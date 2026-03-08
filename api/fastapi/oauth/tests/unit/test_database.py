"""Unit tests for Database class."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from fastapi_oauth_example.adapters.outbound.persistence.database import Database

_DB_URL = "postgresql+asyncpg://user:pass@localhost/test"
_ENGINE_PATH = (
    "fastapi_oauth_example.adapters.outbound.persistence.database.create_async_engine"
)
_MAKER_PATH = (
    "fastapi_oauth_example.adapters.outbound.persistence.database.async_sessionmaker"
)


def _patched_db():
    with patch(_ENGINE_PATH):
        with patch(_MAKER_PATH):
            return Database(_DB_URL)


def _mock_conn_cm():
    conn = AsyncMock()
    cm = AsyncMock()
    cm.__aenter__ = AsyncMock(return_value=conn)
    cm.__aexit__ = AsyncMock(return_value=None)
    return conn, cm


@pytest.mark.unit
class TestDatabase:
    def test_init_creates_engine(self):
        with patch(_ENGINE_PATH) as mock_factory:
            with patch(_MAKER_PATH):
                Database(_DB_URL)
            mock_factory.assert_called_once()

    async def test_create_tables(self):
        db = _patched_db()
        conn, cm = _mock_conn_cm()
        db.engine = MagicMock()
        db.engine.begin.return_value = cm
        await db.create_tables()
        conn.run_sync.assert_called_once()

    async def test_drop_tables(self):
        db = _patched_db()
        conn, cm = _mock_conn_cm()
        db.engine = MagicMock()
        db.engine.begin.return_value = cm
        await db.drop_tables()
        conn.run_sync.assert_called_once()

    async def test_get_session_yields_session(self):
        db = _patched_db()
        mock_session = AsyncMock()
        mock_cm = AsyncMock()
        mock_cm.__aenter__ = AsyncMock(return_value=mock_session)
        mock_cm.__aexit__ = AsyncMock(return_value=None)
        db.async_session_maker = MagicMock(return_value=mock_cm)
        sessions = []
        async for s in db.get_session():
            sessions.append(s)
        assert sessions[0] is mock_session
