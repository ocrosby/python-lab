"""Unit tests for HealthService."""

from datetime import datetime

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
        health_service = HealthService()

        assert health_service.startup_time is not None
        assert isinstance(health_service.startup_time, datetime)

    def test_get_health_status(self):
        """Test get_health_status returns correct status."""
        health_service = HealthService()
        result = health_service.get_health_status()

        assert isinstance(result, HealthCheckDTO)
        assert result.status == "healthy"
        assert result.timestamp is not None

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
        """Test get_detailed_health_status."""
        health_service = HealthService()
        result = await health_service.get_detailed_health_status()

        assert result.status == "healthy"
        assert result.timestamp is not None
        assert result.version == "1.0.0"
        assert result.uptime_seconds >= 0

    @pytest.mark.asyncio
    async def test_get_detailed_health_status_uptime_calculation(self):
        """Test uptime calculation in detailed health status."""
        import time

        health_service = HealthService()
        time.sleep(0.01)
        result = await health_service.get_detailed_health_status()

        assert result.uptime_seconds > 0
        assert result.uptime_seconds >= 0.01
