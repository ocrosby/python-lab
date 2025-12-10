from typing import Optional

from models import Item, ItemInDB
from repository import ItemRepository


class ItemNotFoundException(Exception):
    """Raised when an item is not found in the repository."""
    pass


class ItemService:
    """
    Service layer for item operations.
    
    Provides business logic for CRUD operations on items,
    ensuring proper validation and error handling.
    """
    
    def __init__(self, repository: ItemRepository):
        """
        Initialize the ItemService.
        
        Args:
            repository: Repository for item persistence operations
        """
        self._repository = repository

    def create_item(self, item: Item) -> ItemInDB:
        """
        Create a new item.
        
        Args:
            item: Item data to create
            
        Returns:
            Created item with ID
        """
        return self._repository.create(item)

    def get_item(self, item_id: int) -> ItemInDB:
        """
        Retrieve an item by ID.
        
        Args:
            item_id: ID of item to retrieve
            
        Returns:
            Item with the specified ID
            
        Raises:
            ItemNotFoundException: If item does not exist
        """
        item = self._repository.get_by_id(item_id)
        if item is None:
            raise ItemNotFoundException(f"Item with id {item_id} not found")
        return item

    def get_all_items(self) -> list[ItemInDB]:
        """
        Retrieve all items.
        
        Returns:
            List of all items
        """
        return self._repository.get_all()

    def update_item(self, item_id: int, item: Item) -> ItemInDB:
        """
        Update an existing item.
        
        Args:
            item_id: ID of item to update
            item: New item data
            
        Returns:
            Updated item
            
        Raises:
            ItemNotFoundException: If item does not exist
        """
        updated_item = self._repository.update(item_id, item)
        if updated_item is None:
            raise ItemNotFoundException(f"Item with id {item_id} not found")
        return updated_item

    def delete_item(self, item_id: int) -> None:
        """
        Delete an item.
        
        Args:
            item_id: ID of item to delete
            
        Raises:
            ItemNotFoundException: If item does not exist
        """
        deleted = self._repository.delete(item_id)
        if not deleted:
            raise ItemNotFoundException(f"Item with id {item_id} not found")
