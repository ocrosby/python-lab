"""Test configuration and fixtures."""

import pytest
from fastapi.testclient import TestClient

from src.fastapi_basic_example.main import create_app


@pytest.fixture
def app():
    """Create a FastAPI app instance for testing."""
    return create_app()


@pytest.fixture
def client(app):
    """Create a test client."""
    return TestClient(app)
