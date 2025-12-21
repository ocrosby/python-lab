from .models import Item, ItemInDB
from .repository import ItemRepository
from .exceptions import ItemNotFoundException


class ItemService:
    def __init__(self, repository: ItemRepository):
        self._repository = repository

    def create_item(self, item: Item) -> ItemInDB:
        return self._repository.create(item)

    def get_item(self, item_id: int) -> ItemInDB:
        item = self._repository.get_by_id(item_id)
        if item is None:
            raise ItemNotFoundException(f"Item with id {item_id} not found")
        return item

    def get_all_items(self) -> list[ItemInDB]:
        return self._repository.get_all()

    def update_item(self, item_id: int, item: Item) -> ItemInDB:
        updated_item = self._repository.update(item_id, item)
        if updated_item is None:
            raise ItemNotFoundException(f"Item with id {item_id} not found")
        return updated_item

    def delete_item(self, item_id: int) -> None:
        deleted = self._repository.delete(item_id)
        if not deleted:
            raise ItemNotFoundException(f"Item with id {item_id} not found")
