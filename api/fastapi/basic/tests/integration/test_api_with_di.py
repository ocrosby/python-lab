"""Integration tests for API with dependency injection."""

from unittest.mock import AsyncMock

import pytest
from pytest_mock import MockerFixture

from src.fastapi_basic_example.application.services.health_service import HealthService
from src.fastapi_basic_example.application.use_cases.get_item_use_case import (
    GetItemUseCase,
)
from src.fastapi_basic_example.infrastructure.di.dependencies import (
    get_health_service,
    get_item_use_case,
)


@pytest.mark.integration
class TestAPIWithDI:
    """Test API endpoints with dependency injection mocking."""

    def test_root_endpoint_with_mocked_health_service(
        self, app, client, mocker: MockerFixture
    ):
        """Test root endpoint with mocked health service."""
        from src.fastapi_basic_example.application.dto.item_dto import WelcomeDTO

        mock_health_service = mocker.MagicMock(spec=HealthService)
        mock_health_service.get_welcome_message.return_value = WelcomeDTO(
            Hello="Mocked Hello"
        )

        app.dependency_overrides[get_health_service] = lambda: mock_health_service

        response = client.get("/")

        app.dependency_overrides.clear()

        assert response.status_code == 200
        data = response.json()
        assert data["Hello"] == "Mocked Hello"

    def test_health_endpoint_with_mocked_service(
        self, app, client, mocker: MockerFixture
    ):
        """Test health endpoint with mocked service."""
        from src.fastapi_basic_example.application.dto.item_dto import HealthCheckDTO

        mock_health_service = mocker.MagicMock(spec=HealthService)
        mock_health_service.get_health_status.return_value = HealthCheckDTO(
            status="mocked_healthy", timestamp="2025-11-20T00:00:00Z"
        )

        app.dependency_overrides[get_health_service] = lambda: mock_health_service

        response = client.get("/health")

        app.dependency_overrides.clear()

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "mocked_healthy"
        assert data["timestamp"] == "2025-11-20T00:00:00Z"

    @pytest.mark.asyncio
    async def test_liveness_probe_with_mocked_service(
        self, app, client, mocker: MockerFixture
    ):
        """Test liveness probe with mocked service."""
        mock_health_service = mocker.MagicMock(spec=HealthService)
        mock_health_service.is_alive = AsyncMock(return_value=True)

        app.dependency_overrides[get_health_service] = lambda: mock_health_service

        response = client.get("/health/live")

        app.dependency_overrides.clear()

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "alive"

    @pytest.mark.asyncio
    async def test_readiness_probe_failure_with_mocked_service(
        self, app, client, mocker: MockerFixture
    ):
        """Test readiness probe failure with mocked service."""
        mock_health_service = mocker.MagicMock(spec=HealthService)
        mock_health_service.is_ready = AsyncMock(return_value=False)

        app.dependency_overrides[get_health_service] = lambda: mock_health_service

        response = client.get("/health/ready")

        app.dependency_overrides.clear()

        assert response.status_code == 503
        data = response.json()
        assert "Service not ready" in data["detail"]

    def test_get_item_with_mocked_use_case(self, app, client, mocker: MockerFixture):
        """Test get item endpoint with mocked use case."""
        from src.fastapi_basic_example.application.dto.item_dto import ItemResponseDTO

        mock_use_case = mocker.MagicMock(spec=GetItemUseCase)
        mock_result = ItemResponseDTO(item_id=123, q="test")
        mock_use_case.execute = AsyncMock(return_value=mock_result)

        app.dependency_overrides[get_item_use_case] = lambda: mock_use_case

        response = client.get("/items/123?q=test")

        app.dependency_overrides.clear()

        assert response.status_code == 200
        data = response.json()
        assert data["item_id"] == 123
        assert data["q"] == "test"

        mock_use_case.execute.assert_called_once()
