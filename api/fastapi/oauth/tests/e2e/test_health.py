"""End-to-end tests for health endpoints."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from fastapi_oauth_example.adapters.inbound.http.health_router import get_health_service
from fastapi_oauth_example.main import app


@pytest.mark.e2e
class TestHealthEndpoints:
    def test_health_check_returns_healthy(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data

    def test_liveness_probe_returns_alive(self, client):
        response = client.get("/health/live")
        assert response.status_code == 200
        assert response.json()["status"] == "alive"

    def test_readiness_probe_returns_ready(self, client):
        response = client.get("/health/ready")
        assert response.status_code == 200
        assert response.json()["status"] == "ready"

    def test_startup_probe_returns_started(self, client):
        response = client.get("/health/startup")
        assert response.status_code == 200
        assert response.json()["status"] == "started"

    def test_livez_alias(self, client):
        response = client.get("/livez")
        assert response.status_code == 200

    def test_healthz_alias(self, client):
        response = client.get("/healthz")
        assert response.status_code == 200

    def test_readyz_alias(self, client):
        response = client.get("/readyz")
        assert response.status_code == 200

    def test_liveness_probe_returns_503_when_not_alive(self, client):
        mock_svc = MagicMock()
        mock_svc.is_alive = AsyncMock(return_value=False)
        app.dependency_overrides[get_health_service] = lambda: mock_svc

        response = client.get("/health/live")
        app.dependency_overrides.pop(get_health_service, None)

        assert response.status_code == 503

    def test_readiness_probe_returns_503_when_not_ready(self, client):
        mock_svc = MagicMock()
        mock_svc.is_ready = AsyncMock(return_value=False)
        app.dependency_overrides[get_health_service] = lambda: mock_svc

        response = client.get("/health/ready")
        app.dependency_overrides.pop(get_health_service, None)

        assert response.status_code == 503

    def test_startup_probe_returns_503_when_not_started(self, client):
        mock_svc = MagicMock()
        mock_svc.is_alive = AsyncMock(return_value=False)
        app.dependency_overrides[get_health_service] = lambda: mock_svc

        response = client.get("/health/startup")
        app.dependency_overrides.pop(get_health_service, None)

        assert response.status_code == 503
