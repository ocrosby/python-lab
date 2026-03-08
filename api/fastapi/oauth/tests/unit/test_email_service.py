"""Unit tests for ConsoleEmailService."""

import pytest

from fastapi_oauth_example.application.services.email_service import ConsoleEmailService


@pytest.mark.unit
class TestConsoleEmailService:
    async def test_send_verification_email_prints_token(self, capsys):
        svc = ConsoleEmailService()
        await svc.send_verification_email("user@example.com", "tok123")
        captured = capsys.readouterr()
        assert "tok123" in captured.out
        assert "user@example.com" in captured.out

    async def test_send_password_reset_email_prints_token(self, capsys):
        svc = ConsoleEmailService()
        await svc.send_password_reset_email("user@example.com", "tok456")
        captured = capsys.readouterr()
        assert "tok456" in captured.out
        assert "user@example.com" in captured.out
