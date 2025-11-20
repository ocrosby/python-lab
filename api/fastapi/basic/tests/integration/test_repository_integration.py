"""Integration tests for repository implementations."""

import pytest

from src.fastapi_basic_example.domain.entities.item import Item
from src.fastapi_basic_example.infrastructure.persistence.in_memory_item_repository import (
    InMemoryItemRepository,
)


@pytest.mark.integration
class TestInMemoryItemRepositoryIntegration:
    """Integration test cases for InMemoryItemRepository."""

    @pytest.mark.asyncio
    async def test_repository_workflow(self):
        """Test complete repository workflow."""
        repository = InMemoryItemRepository()

        # Initially empty
        result = await repository.get_by_id(1)
        assert result is None

        # Add an item manually (simulating data persistence)
        item = Item(
            item_id=1, name="Integration Test Item", description="Test Description"
        )
        repository._items[1] = item

        # Retrieve the item
        retrieved_item = await repository.get_by_id(1)
        assert retrieved_item is not None
        assert retrieved_item.item_id == 1
        assert retrieved_item.name == "Integration Test Item"
        assert retrieved_item.description == "Test Description"

    @pytest.mark.asyncio
    async def test_repository_concurrency(self):
        """Test repository behavior under concurrent access simulation."""
        repository = InMemoryItemRepository()

        # Add multiple items
        items = [
            Item(item_id=i, name=f"Item {i}", description=f"Description {i}")
            for i in range(1, 11)
        ]

        for item in items:
            repository._items[item.item_id] = item

        # Retrieve all items
        retrieved_items = []
        for i in range(1, 11):
            item = await repository.get_by_id(i)
            retrieved_items.append(item)

        assert len(retrieved_items) == 10
        assert all(item is not None for item in retrieved_items)
        assert retrieved_items[0].name == "Item 1"
        assert retrieved_items[9].name == "Item 10"
