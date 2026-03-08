"""Test configuration and fixtures."""

import pytest
from fastapi.testclient import TestClient

from src.fastapi_basic_example.adapters.outbound.persistence.in_memory_item_repository import (  # noqa: E501
    InMemoryItemRepository,
)
from src.fastapi_basic_example.domain.entities.item import Item
from src.fastapi_basic_example.infrastructure.di.dependencies import get_item_repository
from src.fastapi_basic_example.main import create_app


@pytest.fixture
def app():
    """Create a FastAPI app instance for testing."""
    return create_app()


@pytest.fixture
def client(app):
    """Create a test client."""
    with TestClient(app, base_url="http://localhost") as c:
        yield c


@pytest.fixture
def seeded_client(app):
    """Create a test client with pre-seeded items (item_id=5 and item_id=10)."""
    repo = InMemoryItemRepository()
    repo._items[5] = Item(item_id=5)
    repo._items[10] = Item(item_id=10)
    app.dependency_overrides[get_item_repository] = lambda: repo
    with TestClient(app, base_url="http://localhost") as c:
        yield c
    app.dependency_overrides.clear()
