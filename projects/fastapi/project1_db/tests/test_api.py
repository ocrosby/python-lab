import pytest
from testcontainers.compose import DockerCompose
import httpx
import time


@pytest.fixture(scope="module")
def compose():
    import os
    compose_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    compose = DockerCompose(compose_path, compose_file_name="compose.yaml", pull=True)
    compose.start()
    
    time.sleep(5)
    
    yield compose
    
    compose.stop()


@pytest.fixture(scope="module")
def api_url(compose):
    return "http://localhost:8080"


def test_read_root(api_url):
    response = httpx.get(f"{api_url}/")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Project1 API"
    assert "links" in data


def test_create_item(api_url):
    item_data = {"name": "Test Item", "description": "Test Description"}
    response = httpx.post(f"{api_url}/api/v1/items", json=item_data)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Item"
    assert data["description"] == "Test Description"
    assert "id" in data
    assert "links" in data
    assert response.headers.get("Cache-Control") == "no-cache"
    assert "Location" in response.headers


def test_get_all_items(api_url):
    response = httpx.get(f"{api_url}/api/v1/items")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert response.headers.get("Cache-Control") == "max-age=60, public"
    if len(response.json()) > 0:
        assert "links" in response.json()[0]


def test_get_item(api_url):
    create_response = httpx.post(
        f"{api_url}/api/v1/items",
        json={"name": "Get Item", "description": "Get Description"}
    )
    item_id = create_response.json()["id"]

    response = httpx.get(f"{api_url}/api/v1/items/{item_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == item_id
    assert data["name"] == "Get Item"
    assert data["description"] == "Get Description"
    assert "links" in data
    assert response.headers.get("Cache-Control") == "max-age=60, public"


def test_get_nonexistent_item(api_url):
    response = httpx.get(f"{api_url}/api/v1/items/99999")
    assert response.status_code == 404


def test_update_item(api_url):
    create_response = httpx.post(
        f"{api_url}/api/v1/items",
        json={"name": "Original", "description": "Original Description"}
    )
    item_id = create_response.json()["id"]

    update_data = {"name": "Updated", "description": "Updated Description"}
    response = httpx.put(f"{api_url}/api/v1/items/{item_id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated"
    assert data["description"] == "Updated Description"
    assert "links" in data
    assert response.headers.get("Cache-Control") == "no-cache"


def test_update_nonexistent_item(api_url):
    response = httpx.put(
        f"{api_url}/api/v1/items/99999",
        json={"name": "Test", "description": "Test"}
    )
    assert response.status_code == 404


def test_delete_item(api_url):
    create_response = httpx.post(
        f"{api_url}/api/v1/items",
        json={"name": "To Delete", "description": "Delete Description"}
    )
    item_id = create_response.json()["id"]

    response = httpx.delete(f"{api_url}/api/v1/items/{item_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == item_id
    assert "links" in data
    assert response.headers.get("Cache-Control") == "no-cache"

    get_response = httpx.get(f"{api_url}/api/v1/items/{item_id}")
    assert get_response.status_code == 404


def test_delete_nonexistent_item(api_url):
    response = httpx.delete(f"{api_url}/api/v1/items/99999")
    assert response.status_code == 404


def test_liveness_endpoint(api_url):
    response = httpx.get(f"{api_url}/health/liveness")
    assert response.status_code == 200
    assert response.json() == {"status": "alive"}


def test_readiness_endpoint(api_url):
    response = httpx.get(f"{api_url}/health/readiness")
    assert response.status_code == 200
    assert response.json() == {"status": "ready"}


def test_startup_endpoint(api_url):
    response = httpx.get(f"{api_url}/health/startup")
    assert response.status_code == 200
    assert response.json() == {"status": "started"}
