"""Item repository interface."""

from abc import ABC, abstractmethod
from typing import Optional

from ..entities.item import Item


class ItemRepository(ABC):
    """Abstract repository for Item entities."""

    @abstractmethod
    async def get_by_id(self, item_id: int) -> Optional[Item]:
        """Get item by ID."""
        pass

    @abstractmethod
    async def save(self, item: Item) -> Item:
        """Save item."""
        pass

    @abstractmethod
    async def delete(self, item_id: int) -> bool:
        """Delete item by ID."""
        pass
