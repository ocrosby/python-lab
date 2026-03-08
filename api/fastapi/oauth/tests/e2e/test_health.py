"""End-to-end tests for health endpoints."""

import pytest


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
