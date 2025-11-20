"""Integration tests for API with dependency injection."""

from unittest.mock import AsyncMock

import pytest
from pytest_mock import MockerFixture

from src.fastapi_basic_example.application.services.health_service import HealthService
from src.fastapi_basic_example.application.use_cases.get_item_use_case import (
    GetItemUseCase,
)


class TestAPIWithDI:
    """Test API endpoints with dependency injection mocking."""

    def test_root_endpoint_with_mocked_health_service(
        self, client, container, mocker: MockerFixture
    ):
        """Test root endpoint with mocked health service."""
        # Mock the health service
        mock_health_service = mocker.MagicMock(spec=HealthService)
        mock_health_service.get_welcome_message.return_value.message = "Mocked Hello"
        mock_health_service.get_welcome_message.return_value.version = "1.0.0"

        # Override the container provider
        with container.health_service.override(mock_health_service):
            response = client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Mocked Hello"

    def test_health_endpoint_with_mocked_service(
        self, client, container, mocker: MockerFixture
    ):
        """Test health endpoint with mocked service."""
        # Mock the health service
        mock_health_service = mocker.MagicMock(spec=HealthService)
        mock_health_service.get_health_status.return_value.status = "mocked_healthy"

        # Override the container provider
        with container.health_service.override(mock_health_service):
            response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "mocked_healthy"

    @pytest.mark.asyncio
    async def test_liveness_probe_with_mocked_service(
        self, client, container, mocker: MockerFixture
    ):
        """Test liveness probe with mocked service."""
        # Mock the health service
        mock_health_service = mocker.MagicMock(spec=HealthService)
        mock_health_service.is_alive = AsyncMock(return_value=True)

        # Override the container provider
        with container.health_service.override(mock_health_service):
            response = client.get("/health/live")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "alive"

    @pytest.mark.asyncio
    async def test_readiness_probe_failure_with_mocked_service(
        self, client, container, mocker: MockerFixture
    ):
        """Test readiness probe failure with mocked service."""
        # Mock the health service to return False for is_ready
        mock_health_service = mocker.MagicMock(spec=HealthService)
        mock_health_service.is_ready = AsyncMock(return_value=False)

        # Override the container provider
        with container.health_service.override(mock_health_service):
            response = client.get("/health/ready")

        assert response.status_code == 503
        data = response.json()
        assert "Service not ready" in data["detail"]

    def test_get_item_with_mocked_use_case(
        self, client, container, mocker: MockerFixture
    ):
        """Test get item endpoint with mocked use case."""
        from src.fastapi_basic_example.application.dto.item_dto import ItemResponseDTO

        # Mock the use case
        mock_use_case = mocker.MagicMock(spec=GetItemUseCase)
        mock_result = ItemResponseDTO(item_id=123, q="test")
        mock_use_case.execute = AsyncMock(return_value=mock_result)

        # Override the container provider
        with container.get_item_use_case.override(mock_use_case):
            response = client.get("/items/123?q=test")

        assert response.status_code == 200
        data = response.json()
        assert data["item_id"] == 123
        assert data["q"] == "test"

        # Verify the use case was called with correct parameters
        mock_use_case.execute.assert_called_once()
