"""Unit tests for application DTOs."""

from datetime import datetime
from uuid import uuid4

import pytest

from fastapi_oauth_example.application.dto.user_dto import (
    EmailVerificationDTO,
    MFASetupResponseDTO,
    MFAVerifyDTO,
    PasswordResetDTO,
    PasswordResetRequestDTO,
    RefreshTokenDTO,
    SessionResponseDTO,
    TokenDTO,
    UserLoginDTO,
    UserRegistrationDTO,
    UserResponseDTO,
)


@pytest.mark.unit
class TestUserRegistrationDTO:
    def test_valid_registration(self):
        dto = UserRegistrationDTO(
            email="user@example.com", username="alice", password="secret"
        )
        assert dto.username == "alice"

    def test_invalid_email_raises(self):
        with pytest.raises(ValueError):
            UserRegistrationDTO(email="bad", username="alice", password="secret")


@pytest.mark.unit
class TestUserLoginDTO:
    def test_login_without_mfa(self):
        dto = UserLoginDTO(username="alice", password="secret")
        assert dto.mfa_code is None

    def test_login_with_mfa(self):
        dto = UserLoginDTO(username="alice", password="secret", mfa_code="123456")
        assert dto.mfa_code == "123456"


@pytest.mark.unit
class TestTokenDTO:
    def test_default_token_type_bearer(self):
        dto = TokenDTO(access_token="acc", refresh_token="ref")
        assert dto.token_type == "bearer"

    def test_fields_set(self):
        dto = TokenDTO(access_token="a", refresh_token="r")
        assert dto.access_token == "a"
        assert dto.refresh_token == "r"


@pytest.mark.unit
class TestRefreshTokenDTO:
    def test_field_set(self):
        dto = RefreshTokenDTO(refresh_token="tok")
        assert dto.refresh_token == "tok"


@pytest.mark.unit
class TestUserResponseDTO:
    def test_all_fields(self):
        uid = uuid4()
        now = datetime.utcnow()
        dto = UserResponseDTO(
            id=uid,
            email="a@b.com",
            username="u",
            is_active=True,
            is_verified=False,
            mfa_enabled=False,
            created_at=now,
            updated_at=now,
        )
        assert dto.id == uid
        assert dto.mfa_enabled is False


@pytest.mark.unit
class TestPasswordResetDTOs:
    def test_request_dto(self):
        dto = PasswordResetRequestDTO(email="x@y.com")
        assert dto.email == "x@y.com"

    def test_reset_dto(self):
        dto = PasswordResetDTO(token="abc", new_password="newpass")
        assert dto.token == "abc"


@pytest.mark.unit
class TestEmailVerificationDTO:
    def test_field_set(self):
        dto = EmailVerificationDTO(token="tok123")
        assert dto.token == "tok123"


@pytest.mark.unit
class TestMFADTOs:
    def test_setup_response(self):
        dto = MFASetupResponseDTO(secret="SEC", qr_code_url="otpauth://totp/...")
        assert dto.secret == "SEC"

    def test_verify_dto(self):
        dto = MFAVerifyDTO(code="123456")
        assert dto.code == "123456"


@pytest.mark.unit
class TestSessionResponseDTO:
    def test_fields(self):
        now = datetime.utcnow()
        dto = SessionResponseDTO(
            id=uuid4(),
            ip_address="127.0.0.1",
            user_agent="pytest",
            last_accessed_at=now,
            created_at=now,
        )
        assert dto.ip_address == "127.0.0.1"

    def test_optional_fields_none(self):
        now = datetime.utcnow()
        dto = SessionResponseDTO(
            id=uuid4(),
            ip_address=None,
            user_agent=None,
            last_accessed_at=now,
            created_at=now,
        )
        assert dto.ip_address is None
