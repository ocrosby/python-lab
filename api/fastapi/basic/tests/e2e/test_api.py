"""End-to-end API tests."""

import pytest
from fastapi.testclient import TestClient

from src.fastapi_basic_example.adapters.outbound.persistence import (
    in_memory_item_repository as repo_module,
)
from src.fastapi_basic_example.domain.entities.item import Item
from src.fastapi_basic_example.infrastructure.di.dependencies import get_item_repository
from src.fastapi_basic_example.main import create_app


@pytest.fixture
def seeded_client():
    """Create a test client with pre-seeded items."""
    repo = repo_module.InMemoryItemRepository()
    repo._items[5] = Item(item_id=5)
    repo._items[10] = Item(item_id=10)
    app = create_app()
    app.dependency_overrides[get_item_repository] = lambda: repo
    return TestClient(app, base_url="http://localhost")


@pytest.mark.e2e
def test_read_root(client):
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"Hello": "World"}


@pytest.mark.e2e
def test_read_item(seeded_client):
    """Test the items endpoint."""
    response = seeded_client.get("/items/5?q=somequery")
    assert response.status_code == 200
    assert response.json() == {"item_id": 5, "q": "somequery"}


@pytest.mark.e2e
def test_read_item_without_query(seeded_client):
    """Test the items endpoint without query parameter."""
    response = seeded_client.get("/items/10")
    assert response.status_code == 200
    assert response.json() == {"item_id": 10, "q": None}


@pytest.mark.e2e
def test_read_item_not_found(client):
    """Test the items endpoint returns 404 for missing items."""
    response = client.get("/items/999")
    assert response.status_code == 404


@pytest.mark.e2e
def test_health_check(client):
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data


@pytest.mark.e2e
def test_readiness_probe(client):
    """Test readiness probe returns 200 when service is ready."""
    response = client.get("/health/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready"
    assert "timestamp" in data


@pytest.mark.e2e
def test_startup_probe(client):
    """Test startup probe returns 200 when service has started."""
    response = client.get("/health/startup")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "started"
    assert "timestamp" in data
