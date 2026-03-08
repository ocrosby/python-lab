"""End-to-end API tests."""

import pytest


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
