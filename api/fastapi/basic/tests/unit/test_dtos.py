"""Unit tests for application DTOs."""

import pytest

from src.fastapi_basic_example.application.dto.item_dto import (
    HealthCheckDTO,
    ItemResponseDTO,
    WelcomeDTO,
)


@pytest.mark.unit
class TestItemResponseDTO:
    """Test cases for ItemResponseDTO."""

    def test_item_response_dto_creation_with_all_fields(self):
        """Test creating ItemResponseDTO with all fields."""
        dto = ItemResponseDTO(item_id=1, q="test query")

        assert dto.item_id == 1
        assert dto.q == "test query"

    def test_item_response_dto_creation_without_query(self):
        """Test creating ItemResponseDTO without query parameter."""
        dto = ItemResponseDTO(item_id=42)

        assert dto.item_id == 42
        assert dto.q is None

    def test_item_response_dto_creation_with_none_query(self):
        """Test creating ItemResponseDTO with explicit None query."""
        dto = ItemResponseDTO(item_id=123, q=None)

        assert dto.item_id == 123
        assert dto.q is None

    def test_item_response_dto_equality(self):
        """Test ItemResponseDTO equality comparison."""
        dto1 = ItemResponseDTO(item_id=1, q="test")
        dto2 = ItemResponseDTO(item_id=1, q="test")
        dto3 = ItemResponseDTO(item_id=2, q="test")
        dto4 = ItemResponseDTO(item_id=1, q="different")

        assert dto1 == dto2
        assert dto1 != dto3
        assert dto1 != dto4


@pytest.mark.unit
class TestHealthCheckDTO:
    """Test cases for HealthCheckDTO."""

    def test_health_check_dto_creation(self):
        """Test creating HealthCheckDTO."""
        dto = HealthCheckDTO()

        assert dto.status == "healthy"

    def test_health_check_dto_equality(self):
        """Test HealthCheckDTO equality comparison."""
        dto1 = HealthCheckDTO()
        dto2 = HealthCheckDTO()

        assert dto1 == dto2
        assert dto1.status == dto2.status


@pytest.mark.unit
class TestWelcomeDTO:
    """Test cases for WelcomeDTO."""

    def test_welcome_dto_creation(self):
        """Test creating WelcomeDTO."""
        dto = WelcomeDTO()

        assert dto.Hello == "World"

    def test_welcome_dto_equality(self):
        """Test WelcomeDTO equality comparison."""
        dto1 = WelcomeDTO()
        dto2 = WelcomeDTO()

        assert dto1 == dto2
        assert dto1.Hello == dto2.Hello
