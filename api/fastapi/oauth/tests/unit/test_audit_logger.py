"""Unit tests for AuditLogger."""

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from fastapi_oauth_example.infrastructure.security.audit_logger import AuditLogger


@pytest.mark.unit
class TestAuditLogger:
    async def test_log_event_adds_and_commits(self):
        session = AsyncMock()
        logger = AuditLogger()
        await logger.log_event(
            session, "login_success", uuid4(), "1.2.3.4", "agent", "details"
        )
        session.add.assert_called_once()
        session.commit.assert_called_once()

    async def test_log_event_with_minimal_args(self):
        session = AsyncMock()
        logger = AuditLogger()
        await logger.log_event(session, "logout")
        session.add.assert_called_once()
        session.commit.assert_called_once()
