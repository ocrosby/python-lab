import pytest
from unittest.mock import Mock
from datetime import datetime, timezone, timedelta
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from auth_service import (
    AuthService,
    UserAlreadyExistsException,
    InvalidRefreshTokenException,
    AuthenticationException
)
from models import UserCreate, UserInDB, RefreshTokenInDB


@pytest.fixture
def mock_user_repository():
    return Mock()


@pytest.fixture
def mock_refresh_token_repository():
    return Mock()


@pytest.fixture
def auth_service(mock_user_repository, mock_refresh_token_repository):
    return AuthService(
        user_repository=mock_user_repository,
        refresh_token_repository=mock_refresh_token_repository,
        secret_key="test-secret-key",
        algorithm="HS256",
        access_token_expire_minutes=30,
        refresh_token_expire_days=7
    )


@pytest.fixture
def sample_user_create():
    return UserCreate(
        email="test@example.com",
        username="testuser",
        password="testpassword123"
    )


@pytest.fixture
def sample_user_in_db():
    return UserInDB(
        id=1,
        email="test@example.com",
        username="testuser",
        hashed_password="$2b$12$hashedpassword",
        is_active=True
    )


def test_verify_password(auth_service):
    hashed = auth_service.get_password_hash("testpassword")
    assert auth_service.verify_password("testpassword", hashed)
    assert not auth_service.verify_password("wrongpassword", hashed)


def test_register_user_success(auth_service, mock_user_repository, sample_user_create, sample_user_in_db):
    mock_user_repository.get_by_username.return_value = None
    mock_user_repository.get_by_email.return_value = None
    mock_user_repository.create.return_value = sample_user_in_db
    
    result = auth_service.register_user(sample_user_create)
    
    assert result == sample_user_in_db
    mock_user_repository.get_by_username.assert_called_once_with("testuser")
    mock_user_repository.get_by_email.assert_called_once_with("test@example.com")
    mock_user_repository.create.assert_called_once()


def test_register_user_duplicate_username(auth_service, mock_user_repository, sample_user_create, sample_user_in_db):
    mock_user_repository.get_by_username.return_value = sample_user_in_db
    
    with pytest.raises(UserAlreadyExistsException) as exc_info:
        auth_service.register_user(sample_user_create)
    
    assert "testuser already exists" in str(exc_info.value)


def test_register_user_duplicate_email(auth_service, mock_user_repository, sample_user_create, sample_user_in_db):
    mock_user_repository.get_by_username.return_value = None
    mock_user_repository.get_by_email.return_value = sample_user_in_db
    
    with pytest.raises(UserAlreadyExistsException) as exc_info:
        auth_service.register_user(sample_user_create)
    
    assert "test@example.com already registered" in str(exc_info.value)


def test_authenticate_user_success(auth_service, mock_user_repository, sample_user_in_db):
    password = "testpassword123"
    hashed = auth_service.get_password_hash(password)
    sample_user_in_db.hashed_password = hashed
    mock_user_repository.get_by_username.return_value = sample_user_in_db
    
    result = auth_service.authenticate_user("testuser", password)
    
    assert result == sample_user_in_db


def test_authenticate_user_wrong_password(auth_service, mock_user_repository, sample_user_in_db):
    password = "testpassword123"
    hashed = auth_service.get_password_hash(password)
    sample_user_in_db.hashed_password = hashed
    mock_user_repository.get_by_username.return_value = sample_user_in_db
    
    result = auth_service.authenticate_user("testuser", "wrongpassword")
    
    assert result is None


def test_authenticate_user_not_found(auth_service, mock_user_repository):
    mock_user_repository.get_by_username.return_value = None
    
    result = auth_service.authenticate_user("nonexistent", "password")
    
    assert result is None


def test_create_access_token(auth_service):
    data = {"sub": "testuser"}
    token = auth_service.create_access_token(data)
    
    assert token is not None
    assert isinstance(token, str)
    
    decoded = auth_service.decode_token(token)
    assert decoded.username == "testuser"


def test_create_token_pair(auth_service, mock_refresh_token_repository, sample_user_in_db):
    mock_refresh_token_repository.create.return_value = Mock()
    
    access_token, refresh_token, token_family = auth_service.create_token_pair(sample_user_in_db)
    
    assert access_token is not None
    assert refresh_token is not None
    assert token_family is not None
    mock_refresh_token_repository.create.assert_called_once()


def test_refresh_access_token_success(
    auth_service,
    mock_refresh_token_repository,
    mock_user_repository,
    sample_user_in_db
):
    stored_token = RefreshTokenInDB(
        id=1,
        user_id=1,
        token="test_refresh_token",
        token_family="test_family",
        expires_at=datetime.now(timezone.utc) + timedelta(days=1),
        created_at=datetime.now(timezone.utc),
        revoked=False
    )
    
    mock_refresh_token_repository.get_by_token.return_value = stored_token
    mock_refresh_token_repository.revoke_by_token.return_value = True
    mock_refresh_token_repository.create.return_value = Mock()
    mock_user_repository.get_by_id.return_value = sample_user_in_db
    
    new_access_token, new_refresh_token = auth_service.refresh_access_token("test_refresh_token")
    
    assert new_access_token is not None
    assert new_refresh_token is not None


def test_refresh_access_token_not_found(auth_service, mock_refresh_token_repository):
    mock_refresh_token_repository.get_by_token.return_value = None
    
    with pytest.raises(InvalidRefreshTokenException) as exc_info:
        auth_service.refresh_access_token("invalid_token")
    
    assert "not found" in str(exc_info.value)


def test_refresh_access_token_revoked(auth_service, mock_refresh_token_repository):
    stored_token = RefreshTokenInDB(
        id=1,
        user_id=1,
        token="test_refresh_token",
        token_family="test_family",
        expires_at=datetime.now(timezone.utc) + timedelta(days=1),
        created_at=datetime.now(timezone.utc),
        revoked=True
    )
    
    mock_refresh_token_repository.get_by_token.return_value = stored_token
    
    with pytest.raises(InvalidRefreshTokenException) as exc_info:
        auth_service.refresh_access_token("test_refresh_token")
    
    assert "revoked" in str(exc_info.value)
    mock_refresh_token_repository.revoke_family.assert_called_once_with("test_family")


def test_refresh_access_token_expired(auth_service, mock_refresh_token_repository):
    stored_token = RefreshTokenInDB(
        id=1,
        user_id=1,
        token="test_refresh_token",
        token_family="test_family",
        expires_at=datetime.now(timezone.utc) - timedelta(days=1),
        created_at=datetime.now(timezone.utc) - timedelta(days=8),
        revoked=False
    )
    
    mock_refresh_token_repository.get_by_token.return_value = stored_token
    
    with pytest.raises(InvalidRefreshTokenException) as exc_info:
        auth_service.refresh_access_token("test_refresh_token")
    
    assert "expired" in str(exc_info.value)


def test_revoke_refresh_token(auth_service, mock_refresh_token_repository):
    mock_refresh_token_repository.revoke_by_token.return_value = True
    
    result = auth_service.revoke_refresh_token("test_token")
    
    assert result is True
    mock_refresh_token_repository.revoke_by_token.assert_called_once_with("test_token")


def test_revoke_all_user_tokens(auth_service, mock_refresh_token_repository):
    mock_refresh_token_repository.revoke_all_for_user.return_value = 3
    
    result = auth_service.revoke_all_user_tokens(1)
    
    assert result == 3
    mock_refresh_token_repository.revoke_all_for_user.assert_called_once_with(1)
