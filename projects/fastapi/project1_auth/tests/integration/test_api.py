import pytest
from testcontainers.compose import DockerCompose
import httpx
import time
import uuid
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from constants import TestConstants


@pytest.fixture(scope="module")
def compose():
    import os
    compose_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    compose = DockerCompose(compose_path, compose_file_name="compose.yaml", pull=True)
    compose.start()
    
    time.sleep(TestConstants.DOCKER_COMPOSE_STARTUP_DELAY)
    
    yield compose
    
    compose.stop()


@pytest.fixture(scope="module")
def api_url(compose):
    return "http://localhost:8080"


@pytest.fixture
def unique_user():
    unique_id = uuid.uuid4().hex[:8]
    return {
        "email": f"test_{unique_id}@example.com",
        "username": f"testuser_{unique_id}",
        "password": "TestPassword123!"
    }


@pytest.fixture
def registered_user(api_url, unique_user):
    response = httpx.post(f"{api_url}/api/v1/auth/register", json=unique_user)
    assert response.status_code == 201
    return unique_user


@pytest.fixture
def auth_token(api_url, registered_user):
    response = httpx.post(
        f"{api_url}/api/v1/auth/token",
        data={
            "username": registered_user["username"],
            "password": registered_user["password"]
        }
    )
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture
def auth_headers(auth_token):
    return {"Authorization": f"Bearer {auth_token}"}


def test_read_root(api_url):
    response = httpx.get(f"{api_url}/")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Project1 API"
    assert "links" in data


# Authentication Tests

def test_auth_register(api_url, unique_user):
    response = httpx.post(f"{api_url}/api/v1/auth/register", json=unique_user)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == unique_user["email"]
    assert data["username"] == unique_user["username"]
    assert "password" not in data
    assert "hashed_password" not in data
    assert data["is_active"] is True
    assert "id" in data
    assert response.headers.get("Cache-Control") == "no-cache"


def test_auth_register_duplicate_username(api_url, registered_user):
    duplicate_user = {
        "email": "different@example.com",
        "username": registered_user["username"],
        "password": "AnotherPassword123!"
    }
    response = httpx.post(f"{api_url}/api/v1/auth/register", json=duplicate_user)
    assert response.status_code == 409
    assert "already exists" in response.json()["detail"].lower()


def test_auth_register_duplicate_email(api_url, registered_user):
    duplicate_user = {
        "email": registered_user["email"],
        "username": "differentuser",
        "password": "AnotherPassword123!"
    }
    response = httpx.post(f"{api_url}/api/v1/auth/register", json=duplicate_user)
    assert response.status_code == 409
    assert "already registered" in response.json()["detail"].lower()


def test_auth_login(api_url, registered_user):
    response = httpx.post(
        f"{api_url}/api/v1/auth/token",
        data={
            "username": registered_user["username"],
            "password": registered_user["password"]
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert response.headers.get("Cache-Control") == "no-cache"


def test_auth_login_invalid_username(api_url):
    response = httpx.post(
        f"{api_url}/api/v1/auth/token",
        data={
            "username": "nonexistentuser",
            "password": "SomePassword123!"
        }
    )
    assert response.status_code == 401
    assert "incorrect" in response.json()["detail"].lower()


def test_auth_login_invalid_password(api_url, registered_user):
    response = httpx.post(
        f"{api_url}/api/v1/auth/token",
        data={
            "username": registered_user["username"],
            "password": "WrongPassword123!"
        }
    )
    assert response.status_code == 401
    assert "incorrect" in response.json()["detail"].lower()


def test_auth_me(api_url, registered_user, auth_headers):
    response = httpx.get(f"{api_url}/api/v1/auth/me", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == registered_user["email"]
    assert data["username"] == registered_user["username"]
    assert data["is_active"] is True
    assert "password" not in data
    assert "hashed_password" not in data
    assert response.headers.get("Cache-Control") == "no-cache"


def test_auth_me_no_token(api_url):
    response = httpx.get(f"{api_url}/api/v1/auth/me")
    assert response.status_code == 401


def test_auth_me_invalid_token(api_url):
    response = httpx.get(
        f"{api_url}/api/v1/auth/me",
        headers={"Authorization": "Bearer invalid_token_here"}
    )
    assert response.status_code == 401


# Item Tests (Protected Endpoints)

def test_create_item_unauthorized(api_url):
    item_data = {"name": "Test Item", "description": "Test Description"}
    response = httpx.post(f"{api_url}/api/v1/items", json=item_data)
    assert response.status_code == 401


def test_create_item(api_url, auth_headers):
    item_data = {"name": "Test Item", "description": "Test Description"}
    response = httpx.post(f"{api_url}/api/v1/items", json=item_data, headers=auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Item"
    assert data["description"] == "Test Description"
    assert "id" in data
    assert "links" in data
    assert response.headers.get("Cache-Control") == "no-cache"
    assert "Location" in response.headers


def test_get_all_items_unauthorized(api_url):
    response = httpx.get(f"{api_url}/api/v1/items")
    assert response.status_code == 401


def test_get_all_items(api_url, auth_headers):
    response = httpx.get(f"{api_url}/api/v1/items", headers=auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert response.headers.get("Cache-Control") == "max-age=60, public"
    if len(response.json()) > 0:
        assert "links" in response.json()[0]


def test_get_item_unauthorized(api_url, auth_headers):
    create_response = httpx.post(
        f"{api_url}/api/v1/items",
        json={"name": "Get Item", "description": "Get Description"},
        headers=auth_headers
    )
    item_id = create_response.json()["id"]
    
    response = httpx.get(f"{api_url}/api/v1/items/{item_id}")
    assert response.status_code == 401


def test_get_item(api_url, auth_headers):
    create_response = httpx.post(
        f"{api_url}/api/v1/items",
        json={"name": "Get Item", "description": "Get Description"},
        headers=auth_headers
    )
    item_id = create_response.json()["id"]

    response = httpx.get(f"{api_url}/api/v1/items/{item_id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == item_id
    assert data["name"] == "Get Item"
    assert data["description"] == "Get Description"
    assert "links" in data
    assert response.headers.get("Cache-Control") == "max-age=60, public"


def test_get_nonexistent_item(api_url, auth_headers):
    response = httpx.get(f"{api_url}/api/v1/items/99999", headers=auth_headers)
    assert response.status_code == 404


def test_update_item_unauthorized(api_url, auth_headers):
    create_response = httpx.post(
        f"{api_url}/api/v1/items",
        json={"name": "Original", "description": "Original Description"},
        headers=auth_headers
    )
    item_id = create_response.json()["id"]

    update_data = {"name": "Updated", "description": "Updated Description"}
    response = httpx.put(f"{api_url}/api/v1/items/{item_id}", json=update_data)
    assert response.status_code == 401


def test_update_item(api_url, auth_headers):
    create_response = httpx.post(
        f"{api_url}/api/v1/items",
        json={"name": "Original", "description": "Original Description"},
        headers=auth_headers
    )
    item_id = create_response.json()["id"]

    update_data = {"name": "Updated", "description": "Updated Description"}
    response = httpx.put(f"{api_url}/api/v1/items/{item_id}", json=update_data, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated"
    assert data["description"] == "Updated Description"
    assert "links" in data
    assert response.headers.get("Cache-Control") == "no-cache"


def test_update_nonexistent_item(api_url, auth_headers):
    response = httpx.put(
        f"{api_url}/api/v1/items/99999",
        json={"name": "Test", "description": "Test"},
        headers=auth_headers
    )
    assert response.status_code == 404


def test_delete_item_unauthorized(api_url, auth_headers):
    create_response = httpx.post(
        f"{api_url}/api/v1/items",
        json={"name": "To Delete", "description": "Delete Description"},
        headers=auth_headers
    )
    item_id = create_response.json()["id"]

    response = httpx.delete(f"{api_url}/api/v1/items/{item_id}")
    assert response.status_code == 401


def test_delete_item(api_url, auth_headers):
    create_response = httpx.post(
        f"{api_url}/api/v1/items",
        json={"name": "To Delete", "description": "Delete Description"},
        headers=auth_headers
    )
    item_id = create_response.json()["id"]

    response = httpx.delete(f"{api_url}/api/v1/items/{item_id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == item_id
    assert "links" in data
    assert response.headers.get("Cache-Control") == "no-cache"

    get_response = httpx.get(f"{api_url}/api/v1/items/{item_id}", headers=auth_headers)
    assert get_response.status_code == 404


def test_delete_nonexistent_item(api_url, auth_headers):
    response = httpx.delete(f"{api_url}/api/v1/items/99999", headers=auth_headers)
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
