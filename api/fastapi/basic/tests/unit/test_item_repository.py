"""Unit tests for Repo."""

import pytest

from src.fastapi_basic_example.domain.entities.item import Item
from src.fastapi_basic_example.infrastructure.persistence import (
    in_memory_item_repository,
)

Repo = in_memory_item_repository.InMemoryItemRepository


@pytest.mark.unit
class TestRepo:
    """Test cases for Repo."""

    def test_init(self):
        """Test repository initialization."""
        repository = Repo()
        assert repository._items == {}

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self):
        """Test getting an item that doesn't exist."""
        repository = Repo()
        result = await repository.get_by_id(999)
        assert result is None

    @pytest.mark.asyncio
    async def test_get_by_id_found(self):
        """Test getting an item that exists."""
        repository = Repo()
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
        repository = Repo()
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

    @pytest.mark.asyncio
    async def test_save_item(self):
        """Test saving an item."""
        repository = Repo()
        item = Item(item_id=1, name="Test Item", description="Test Description")

        saved = await repository.save(item)

        assert saved == item
        assert saved.item_id == 1
        assert await repository.get_by_id(1) == saved

    @pytest.mark.asyncio
    async def test_save_overwrites_existing(self):
        """Test saving overwrites existing item."""
        repository = Repo()
        item1 = Item(item_id=1, name="Original", description="Original Desc")
        item2 = Item(item_id=1, name="Updated", description="Updated Desc")

        await repository.save(item1)
        await repository.save(item2)

        result = await repository.get_by_id(1)
        assert result == item2
        assert result.name == "Updated"

    @pytest.mark.asyncio
    async def test_delete_existing_item(self):
        """Test deleting an existing item."""
        repository = Repo()
        item = Item(item_id=1, name="Test Item", description="Test Description")
        await repository.save(item)

        result = await repository.delete(1)

        assert result is True
        assert await repository.get_by_id(1) is None

    @pytest.mark.asyncio
    async def test_delete_non_existing_item(self):
        """Test deleting a non-existing item."""
        repository = Repo()

        result = await repository.delete(999)

        assert result is False
