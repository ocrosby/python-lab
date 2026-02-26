"""End-to-end API tests."""

import pytest


@pytest.mark.e2e
def test_read_root(client):
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"Hello": "World"}


@pytest.mark.e2e
def test_read_item(client):
    """Test the items endpoint."""
    response = client.get("/items/5?q=somequery")
    assert response.status_code == 200
    assert response.json() == {"item_id": 5, "q": "somequery"}


@pytest.mark.e2e
def test_read_item_without_query(client):
    """Test the items endpoint without query parameter."""
    response = client.get("/items/10")
    assert response.status_code == 200
    assert response.json() == {"item_id": 10, "q": None}


@pytest.mark.e2e
def test_health_check(client):
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data
