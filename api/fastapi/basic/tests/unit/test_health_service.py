"""Unit tests for HealthService."""

from datetime import UTC, datetime
from unittest.mock import patch

import pytest
from pytest_mock import MockerFixture

from src.fastapi_basic_example.application.dto.item_dto import (
    HealthCheckDTO,
    WelcomeDTO,
)
from src.fastapi_basic_example.application.services.health_service import HealthService


@pytest.mark.unit
class TestHealthService:
    """Test cases for HealthService."""

    def test_init(self):
        """Test health service initialization."""
        with patch(
            "src.fastapi_basic_example.application.services.health_service.datetime"
        ) as mock_dt:
            mock_startup_time = datetime(2024, 1, 1, 0, 0, 0, tzinfo=UTC)
            mock_dt.now.return_value = mock_startup_time

            health_service = HealthService()

            assert health_service.startup_time == mock_startup_time

    def test_get_health_status(self):
        """Test get_health_status returns correct status."""
        health_service = HealthService()
        result = health_service.get_health_status()

        assert isinstance(result, HealthCheckDTO)
        assert result.status == "healthy"

    def test_get_welcome_message(self):
        """Test get_welcome_message returns correct message."""
        health_service = HealthService()
        result = health_service.get_welcome_message()

        assert isinstance(result, WelcomeDTO)
        assert result.Hello == "World"

    @pytest.mark.asyncio
    async def test_is_alive(self):
        """Test is_alive returns True."""
        health_service = HealthService()
        result = await health_service.is_alive()

        assert result is True

    @pytest.mark.asyncio
    async def test_is_ready(self):
        """Test is_ready returns True."""
        health_service = HealthService()
        result = await health_service.is_ready()

        assert result is True

    @pytest.mark.asyncio
    async def test_get_detailed_health_status(self, mocker: MockerFixture):
        """Test get_detailed_health_status with mocked datetime."""
        # Mock the startup time and current time
        startup_time = datetime(2024, 1, 1, 0, 0, 0, tzinfo=UTC)
        current_time = datetime(2024, 1, 1, 0, 5, 0, tzinfo=UTC)  # 5 minutes later

        with patch(
            "src.fastapi_basic_example.application.services.health_service.datetime"
        ) as mock_dt:
            # Mock the startup time during initialization
            mock_dt.now.return_value = startup_time
            health_service = HealthService()

            # Mock the current time during the method call
            mock_dt.now.return_value = current_time
            current_time.isoformat.return_value = "2024-01-01T00:05:00+00:00"

            result = await health_service.get_detailed_health_status()

            assert result["status"] == "healthy"
            assert result["timestamp"] == "2024-01-01T00:05:00+00:00"
            assert result["version"] == "1.0.0"
            assert result["uptime_seconds"] == 300.0  # 5 minutes

    @pytest.mark.asyncio
    async def test_get_detailed_health_status_uptime_calculation(self):
        """Test uptime calculation in detailed health status."""
        with patch(
            "src.fastapi_basic_example.application.services.health_service.datetime"
        ) as mock_dt:
            startup_time = datetime(2024, 1, 1, 0, 0, 0, tzinfo=UTC)
            current_time = datetime(
                2024, 1, 1, 1, 30, 45, tzinfo=UTC
            )  # 1.5 hours later

            mock_dt.now.return_value = startup_time
            health_service = HealthService()

            mock_dt.now.return_value = current_time
            current_time.isoformat.return_value = "2024-01-01T01:30:45+00:00"

            result = await health_service.get_detailed_health_status()

            expected_uptime = (current_time - startup_time).total_seconds()
            assert result["uptime_seconds"] == expected_uptime
            assert result["uptime_seconds"] == 5445.0  # 1 hour 30 minutes 45 seconds
