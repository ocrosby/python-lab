import pytest
from testcontainers.core.container import DockerContainer
from testcontainers.core.wait_strategies import LogMessageWaitStrategy
import httpx


@pytest.fixture(scope="module")
def api_container():
    container = (
        DockerContainer("project1:latest")
        .with_exposed_ports(8000)
        .with_env("PYTHONUNBUFFERED", "1")
        .waiting_for(LogMessageWaitStrategy("Application startup complete"))
    )
    container.start()

    yield container

    container.stop()


@pytest.fixture(scope="module")
def api_url(api_container):
    host = api_container.get_container_host_ip()
    port = api_container.get_exposed_port(8000)
    return f"http://{host}:{port}"


def test_read_root(api_url):
    response = httpx.get(f"{api_url}/")
    assert response.status_code == 200
    assert response.json() == {"Hello": "World"}


def test_read_item(api_url):
    response = httpx.get(f"{api_url}/items/42?q=test")
    assert response.status_code == 200
    assert response.json() == {"item_id": 42, "q": "test"}


def test_read_item_without_query(api_url):
    response = httpx.get(f"{api_url}/items/100")
    assert response.status_code == 200
    assert response.json() == {"item_id": 100, "q": None}


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
