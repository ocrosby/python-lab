"""In-memory implementation of item repository."""

from typing import Dict, Optional

from ...domain.entities.item import Item
from ...domain.repositories.item_repository import ItemRepository


class InMemoryItemRepository(ItemRepository):
    """In-memory implementation of ItemRepository."""

    def __init__(self):
        self._items: Dict[int, Item] = {}

    async def get_by_id(self, item_id: int) -> Optional[Item]:
        """Get item by ID."""
        return self._items.get(item_id)

    async def save(self, item: Item) -> Item:
        """Save item."""
        self._items[item.item_id] = item
        return item

    async def delete(self, item_id: int) -> bool:
        """Delete item by ID."""
        if item_id in self._items:
            del self._items[item_id]
            return True
        return False
