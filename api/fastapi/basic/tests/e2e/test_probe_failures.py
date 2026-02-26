"""E2E tests for probe endpoint failure scenarios."""

from unittest.mock import AsyncMock

import pytest

from src.fastapi_basic_example.application.services.health_service import HealthService
from src.fastapi_basic_example.infrastructure.di.dependencies import (
    get_health_service,
)


@pytest.mark.e2e
class TestProbeFailures:
    """Test probe endpoint failure scenarios."""

    def test_liveness_probe_failure(self, app, client, mocker):
        """Test liveness probe when service is not alive."""
        mock_service = mocker.MagicMock(spec=HealthService)
        mock_service.is_alive = AsyncMock(return_value=False)

        app.dependency_overrides[get_health_service] = lambda: mock_service

        response = client.get("/health/live")

        app.dependency_overrides.clear()

        assert response.status_code == 503
        assert "not alive" in response.json()["detail"]

    def test_healthz_probe_failure(self, app, client, mocker):
        """Test healthz endpoint when service is not alive."""
        mock_service = mocker.MagicMock(spec=HealthService)
        mock_service.is_alive = AsyncMock(return_value=False)

        app.dependency_overrides[get_health_service] = lambda: mock_service

        response = client.get("/healthz")

        app.dependency_overrides.clear()

        assert response.status_code == 503
        assert "not alive" in response.json()["detail"]

    def test_readiness_probe_failure(self, app, client, mocker):
        """Test readiness probe when service is not ready."""
        mock_service = mocker.MagicMock(spec=HealthService)
        mock_service.is_ready = AsyncMock(return_value=False)

        app.dependency_overrides[get_health_service] = lambda: mock_service

        response = client.get("/health/ready")

        app.dependency_overrides.clear()

        assert response.status_code == 503
        assert "not ready" in response.json()["detail"]

    def test_readiness_endpoint_failure(self, app, client, mocker):
        """Test /readiness endpoint when service is not ready."""
        mock_service = mocker.MagicMock(spec=HealthService)
        mock_service.is_ready = AsyncMock(return_value=False)

        app.dependency_overrides[get_health_service] = lambda: mock_service

        response = client.get("/readiness")

        app.dependency_overrides.clear()

        assert response.status_code == 503
        assert "not ready" in response.json()["detail"]

    def test_startup_probe_failure(self, app, client, mocker):
        """Test startup probe when service is not started."""
        mock_service = mocker.MagicMock(spec=HealthService)
        mock_service.is_alive = AsyncMock(return_value=False)

        app.dependency_overrides[get_health_service] = lambda: mock_service

        response = client.get("/health/startup")

        app.dependency_overrides.clear()

        assert response.status_code == 503
        assert "not started" in response.json()["detail"]
