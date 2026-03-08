"""Shared test fixtures for all test layers."""

from datetime import datetime
from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from fastapi_oauth_example.application.dto.user_dto import UserResponseDTO
from fastapi_oauth_example.infrastructure.di.dependencies import get_current_user
from fastapi_oauth_example.main import app


@pytest.fixture
def client():
    """Test client with mocked DB lifespan."""
    with patch(
        "fastapi_oauth_example.infrastructure.di.dependencies.database.create_tables",
        new_callable=AsyncMock,
    ):
        with TestClient(app, base_url="http://localhost") as c:
            yield c
    app.dependency_overrides.clear()


@pytest.fixture
def mock_current_user():
    """A valid authenticated UserResponseDTO for use in route tests."""
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


@pytest.fixture
def authenticated_client(client, mock_current_user):
    """Client with get_current_user dependency overridden."""
    app.dependency_overrides[get_current_user] = lambda: mock_current_user
    yield client
    app.dependency_overrides.pop(get_current_user, None)
