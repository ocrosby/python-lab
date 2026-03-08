"""Unit tests for LogoutUseCase."""

from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from fastapi_oauth_example.application.use_cases.logout_use_case import LogoutUseCase


@pytest.fixture
def deps():
    blacklist = MagicMock()
    blacklist.blacklist_token = AsyncMock()

    refresh_repo = MagicMock()
    refresh_repo.revoke = AsyncMock()

    jwt = MagicMock()
    exp = int((datetime.utcnow() + timedelta(hours=1)).timestamp())
    jwt.decode_token = MagicMock(return_value={"exp": exp, "sub": "alice"})

    audit = MagicMock()
    audit.log_event = AsyncMock()

    session = MagicMock()

    return {
        "token_blacklist": blacklist,
        "refresh_token_repo": refresh_repo,
        "jwt_handler": jwt,
        "audit_logger": audit,
        "db_session": session,
    }


@pytest.mark.unit
class TestLogoutUseCase:
    async def test_blacklists_access_token(self, deps):
        uc = LogoutUseCase(**deps)
        await uc.execute("access_tok", uuid4())
        deps["token_blacklist"].blacklist_token.assert_called_once()

    async def test_revokes_refresh_token_when_provided(self, deps):
        uc = LogoutUseCase(**deps)
        await uc.execute("access_tok", uuid4(), refresh_token="refresh_tok")
        deps["refresh_token_repo"].revoke.assert_called_once_with("refresh_tok")

    async def test_does_not_revoke_when_no_refresh_token(self, deps):
        uc = LogoutUseCase(**deps)
        await uc.execute("access_tok", uuid4())
        deps["refresh_token_repo"].revoke.assert_not_called()

    async def test_logs_audit_event(self, deps):
        uc = LogoutUseCase(**deps)
        user_id = uuid4()
        await uc.execute("access_tok", user_id, ip_address="1.2.3.4")
        deps["audit_logger"].log_event.assert_called_once()

    async def test_blacklist_uses_exp_from_payload(self, deps):
        exp = int((datetime.utcnow() + timedelta(hours=2)).timestamp())
        deps["jwt_handler"].decode_token = MagicMock(return_value={"exp": exp})
        uc = LogoutUseCase(**deps)
        await uc.execute("access_tok", uuid4())
        call_args = deps["token_blacklist"].blacklist_token.call_args[0]
        expires_at: datetime = call_args[2]
        assert expires_at > datetime.utcnow()

    async def test_blacklist_uses_utcnow_when_no_payload(self, deps):
        deps["jwt_handler"].decode_token = MagicMock(return_value=None)
        uc = LogoutUseCase(**deps)
        await uc.execute("access_tok", uuid4())
        deps["token_blacklist"].blacklist_token.assert_called_once()
