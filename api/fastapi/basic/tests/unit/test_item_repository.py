"""Unit tests for InMemoryItemRepository."""

import pytest

from src.fastapi_basic_example.domain.entities.item import Item
from src.fastapi_basic_example.infrastructure.persistence.in_memory_item_repository import (
    InMemoryItemRepository,
)


@pytest.mark.unit
class TestInMemoryItemRepository:
    """Test cases for InMemoryItemRepository."""

    def test_init(self):
        """Test repository initialization."""
        repository = InMemoryItemRepository()
        assert repository._items == {}

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self):
        """Test getting an item that doesn't exist."""
        repository = InMemoryItemRepository()
        result = await repository.get_by_id(999)
        assert result is None

    @pytest.mark.asyncio
    async def test_get_by_id_found(self):
        """Test getting an item that exists."""
        repository = InMemoryItemRepository()
        item = Item(item_id=1, name="Test Item", description="Test Description")
        repository._items[1] = item

        result = await repository.get_by_id(1)
        assert result == item
        assert result.item_id == 1
        assert result.name == "Test Item"
        assert result.description == "Test Description"

    @pytest.mark.asyncio
    async def test_multiple_items(self):
        """Test repository with multiple items."""
        repository = InMemoryItemRepository()
        item1 = Item(item_id=1, name="Item 1", description="Description 1")
        item2 = Item(item_id=2, name="Item 2", description="Description 2")

        repository._items[1] = item1
        repository._items[2] = item2

        result1 = await repository.get_by_id(1)
        result2 = await repository.get_by_id(2)
        result3 = await repository.get_by_id(3)

        assert result1 == item1
        assert result2 == item2
        assert result3 is None
