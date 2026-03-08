"""Unit tests for HealthService."""

import pytest

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

        assert health_service is not None

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

