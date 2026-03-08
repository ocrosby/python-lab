"""Integration tests for auth HTTP routes with mocked use cases."""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from fastapi_oauth_example.application.dto.user_dto import (
    MFASetupResponseDTO,
    SessionResponseDTO,
    TokenDTO,
    UserResponseDTO,
)
from fastapi_oauth_example.infrastructure.di.dependencies import (
    get_enable_mfa_use_case,
    get_list_sessions_use_case,
    get_login_user_use_case,
    get_logout_use_case,
    get_refresh_token_use_case,
    get_register_user_use_case,
    get_request_password_reset_use_case,
    get_reset_password_use_case,
    get_revoke_session_use_case,
    get_send_email_verification_use_case,
    get_setup_mfa_use_case,
    get_verify_email_use_case,
    oauth2_scheme,
)
from fastapi_oauth_example.main import app


def make_user_response():
    return UserResponseDTO(
        id=uuid4(),
        email="test@example.com",
        username="testuser",
        is_active=True,
        is_verified=True,
        mfa_enabled=False,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )


def make_token():
    return TokenDTO(access_token="acc_tok", refresh_token="ref_tok")


@pytest.mark.integration
class TestRegisterRoute:
    def test_register_returns_201(self, client):
        mock_uc = MagicMock()
        mock_uc.execute = AsyncMock(return_value=make_user_response())
        app.dependency_overrides[get_register_user_use_case] = lambda: mock_uc

        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "new@example.com",
                "username": "newuser",
                "password": "pass",
            },
        )
        app.dependency_overrides.pop(get_register_user_use_case, None)

        assert response.status_code == 201
        assert response.json()["username"] == "testuser"

    def test_register_returns_400_on_duplicate(self, client):
        mock_uc = MagicMock()
        mock_uc.execute = AsyncMock(side_effect=ValueError("Email already registered"))
        app.dependency_overrides[get_register_user_use_case] = lambda: mock_uc

        response = client.post(
            "/api/v1/auth/register",
            json={"email": "taken@example.com", "username": "user", "password": "pass"},
        )
        app.dependency_overrides.pop(get_register_user_use_case, None)

        assert response.status_code == 400
        assert "Email already registered" in response.json()["detail"]


@pytest.mark.integration
class TestLoginRoute:
    def test_login_returns_200_with_tokens(self, client):
        mock_uc = MagicMock()
        mock_uc.execute = AsyncMock(return_value=make_token())
        app.dependency_overrides[get_login_user_use_case] = lambda: mock_uc

        response = client.post(
            "/api/v1/auth/login",
            json={"username": "alice", "password": "pass"},
        )
        app.dependency_overrides.pop(get_login_user_use_case, None)

        assert response.status_code == 200
        data = response.json()
        assert data["access_token"] == "acc_tok"
        assert data["token_type"] == "bearer"

    def test_login_returns_401_for_invalid_credentials(self, client):
        mock_uc = MagicMock()
        mock_uc.execute = AsyncMock(side_effect=ValueError("Invalid credentials"))
        app.dependency_overrides[get_login_user_use_case] = lambda: mock_uc

        response = client.post(
            "/api/v1/auth/login",
            json={"username": "alice", "password": "wrong"},
        )
        app.dependency_overrides.pop(get_login_user_use_case, None)

        assert response.status_code == 401

    def test_login_returns_401_for_locked_account(self, client):
        mock_uc = MagicMock()
        mock_uc.execute = AsyncMock(side_effect=ValueError("Account is locked"))
        app.dependency_overrides[get_login_user_use_case] = lambda: mock_uc

        response = client.post(
            "/api/v1/auth/login",
            json={"username": "alice", "password": "pass"},
        )
        app.dependency_overrides.pop(get_login_user_use_case, None)

        assert response.status_code == 401


@pytest.mark.integration
class TestMeRoute:
    def test_me_returns_user_when_authenticated(self, authenticated_client):
        response = authenticated_client.get("/api/v1/auth/me")
        assert response.status_code == 200
        assert response.json()["username"] == "testuser"

    def test_me_returns_401_without_token(self, client):
        response = client.get("/api/v1/auth/me")
        assert response.status_code == 401


@pytest.mark.integration
class TestLogoutRoute:
    def test_logout_returns_204(self, authenticated_client):
        mock_uc = MagicMock()
        mock_uc.execute = AsyncMock()
        app.dependency_overrides[get_logout_use_case] = lambda: mock_uc
        app.dependency_overrides[oauth2_scheme] = lambda: "test_access_token"

        response = authenticated_client.post("/api/v1/auth/logout")
        app.dependency_overrides.pop(get_logout_use_case, None)
        app.dependency_overrides.pop(oauth2_scheme, None)

        assert response.status_code == 204


@pytest.mark.integration
class TestRefreshRoute:
    def test_refresh_returns_200(self, client):
        mock_uc = MagicMock()
        mock_uc.execute = AsyncMock(return_value=make_token())
        app.dependency_overrides[get_refresh_token_use_case] = lambda: mock_uc

        response = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": "ref_tok"},
        )
        app.dependency_overrides.pop(get_refresh_token_use_case, None)

        assert response.status_code == 200
        assert response.json()["access_token"] == "acc_tok"

    def test_refresh_returns_401_for_invalid_token(self, client):
        mock_uc = MagicMock()
        mock_uc.execute = AsyncMock(
            side_effect=ValueError("Refresh token has been revoked")
        )
        app.dependency_overrides[get_refresh_token_use_case] = lambda: mock_uc

        response = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": "bad_tok"},
        )
        app.dependency_overrides.pop(get_refresh_token_use_case, None)

        assert response.status_code == 401


@pytest.mark.integration
class TestPasswordResetRoutes:
    def test_request_reset_returns_204(self, client):
        mock_uc = MagicMock()
        mock_uc.execute = AsyncMock()
        app.dependency_overrides[get_request_password_reset_use_case] = lambda: mock_uc

        response = client.post(
            "/api/v1/auth/password-reset/request",
            json={"email": "user@example.com"},
        )
        app.dependency_overrides.pop(get_request_password_reset_use_case, None)

        assert response.status_code == 204

    def test_confirm_reset_returns_204(self, client):
        mock_uc = MagicMock()
        mock_uc.execute = AsyncMock()
        app.dependency_overrides[get_reset_password_use_case] = lambda: mock_uc

        response = client.post(
            "/api/v1/auth/password-reset/confirm",
            json={"token": "tok", "new_password": "newpass"},
        )
        app.dependency_overrides.pop(get_reset_password_use_case, None)

        assert response.status_code == 204

    def test_confirm_reset_returns_400_for_invalid_token(self, client):
        mock_uc = MagicMock()
        mock_uc.execute = AsyncMock(side_effect=ValueError("Invalid or expired token"))
        app.dependency_overrides[get_reset_password_use_case] = lambda: mock_uc

        response = client.post(
            "/api/v1/auth/password-reset/confirm",
            json={"token": "bad", "new_password": "newpass"},
        )
        app.dependency_overrides.pop(get_reset_password_use_case, None)

        assert response.status_code == 400


@pytest.mark.integration
class TestEmailVerificationRoutes:
    def test_verify_email_returns_204(self, client):
        mock_uc = MagicMock()
        mock_uc.execute = AsyncMock()
        app.dependency_overrides[get_verify_email_use_case] = lambda: mock_uc

        response = client.post(
            "/api/v1/auth/email/verify",
            json={"token": "tok"},
        )
        app.dependency_overrides.pop(get_verify_email_use_case, None)

        assert response.status_code == 204

    def test_resend_verification_returns_204(self, authenticated_client):
        mock_uc = MagicMock()
        mock_uc.execute = AsyncMock()
        app.dependency_overrides[get_send_email_verification_use_case] = lambda: mock_uc

        response = authenticated_client.post("/api/v1/auth/email/resend-verification")
        app.dependency_overrides.pop(get_send_email_verification_use_case, None)

        assert response.status_code == 204


@pytest.mark.integration
class TestMFARoutes:
    def test_mfa_setup_returns_200(self, authenticated_client):
        mock_uc = MagicMock()
        mock_uc.execute = AsyncMock(
            return_value=MFASetupResponseDTO(
                secret="SECRET", qr_code_url="otpauth://totp/..."
            )
        )
        app.dependency_overrides[get_setup_mfa_use_case] = lambda: mock_uc

        response = authenticated_client.post("/api/v1/auth/mfa/setup")
        app.dependency_overrides.pop(get_setup_mfa_use_case, None)

        assert response.status_code == 200
        assert response.json()["secret"] == "SECRET"

    def test_mfa_verify_returns_204(self, authenticated_client):
        mock_uc = MagicMock()
        mock_uc.execute = AsyncMock()
        app.dependency_overrides[get_enable_mfa_use_case] = lambda: mock_uc

        response = authenticated_client.post(
            "/api/v1/auth/mfa/verify", json={"code": "123456"}
        )
        app.dependency_overrides.pop(get_enable_mfa_use_case, None)

        assert response.status_code == 204


@pytest.mark.integration
class TestSessionRoutes:
    def test_list_sessions_returns_200(self, authenticated_client):
        now = datetime.utcnow()
        mock_uc = MagicMock()
        mock_uc.execute = AsyncMock(
            return_value=[
                SessionResponseDTO(
                    id=uuid4(),
                    ip_address="127.0.0.1",
                    user_agent="test",
                    last_accessed_at=now,
                    created_at=now,
                )
            ]
        )
        app.dependency_overrides[get_list_sessions_use_case] = lambda: mock_uc

        response = authenticated_client.get("/api/v1/auth/sessions")
        app.dependency_overrides.pop(get_list_sessions_use_case, None)

        assert response.status_code == 200
        assert len(response.json()) == 1

    def test_revoke_session_returns_204(self, authenticated_client):
        mock_uc = MagicMock()
        mock_uc.execute = AsyncMock()
        app.dependency_overrides[get_revoke_session_use_case] = lambda: mock_uc

        response = authenticated_client.delete(f"/api/v1/auth/sessions/{uuid4()}")
        app.dependency_overrides.pop(get_revoke_session_use_case, None)

        assert response.status_code == 204

    def test_revoke_session_returns_404_for_unknown(self, authenticated_client):
        mock_uc = MagicMock()
        mock_uc.execute = AsyncMock(side_effect=ValueError("Session not found"))
        app.dependency_overrides[get_revoke_session_use_case] = lambda: mock_uc

        response = authenticated_client.delete(f"/api/v1/auth/sessions/{uuid4()}")
        app.dependency_overrides.pop(get_revoke_session_use_case, None)

        assert response.status_code == 404
