from abc import ABC, abstractmethod
from typing import Optional
from psycopg2.extras import RealDictCursor

from domain.items.models import Item, ItemInDB
from infrastructure.database import ConnectionManager, BaseRepository, RepositoryException


class ItemCreationException(RepositoryException):
    pass


class ItemRepository(ABC):
    @abstractmethod
    def create(self, item: Item) -> ItemInDB:
        pass

    @abstractmethod
    def get_by_id(self, item_id: int) -> Optional[ItemInDB]:
        pass

    @abstractmethod
    def get_all(self) -> list[ItemInDB]:
        pass

    @abstractmethod
    def update(self, item_id: int, item: Item) -> Optional[ItemInDB]:
        pass

    @abstractmethod
    def delete(self, item_id: int) -> bool:
        pass


class InMemoryItemRepository(ItemRepository):
    def __init__(self):
        self._items: dict[int, Item] = {}
        self._next_id = 1

    def create(self, item: Item) -> ItemInDB:
        item_id = self._next_id
        self._items[item_id] = item
        self._next_id += 1
        return ItemInDB(id=item_id, name=item.name, description=item.description)

    def get_by_id(self, item_id: int) -> Optional[ItemInDB]:
        item = self._items.get(item_id)
        if item is None:
            return None
        return ItemInDB(id=item_id, name=item.name, description=item.description)

    def get_all(self) -> list[ItemInDB]:
        return [
            ItemInDB(id=item_id, name=item.name, description=item.description)
            for item_id, item in self._items.items()
        ]

    def update(self, item_id: int, item: Item) -> Optional[ItemInDB]:
        if item_id not in self._items:
            return None
        self._items[item_id] = item
        return ItemInDB(id=item_id, name=item.name, description=item.description)

    def delete(self, item_id: int) -> bool:
        if item_id not in self._items:
            return False
        del self._items[item_id]
        return True


class PostgresItemRepository(BaseRepository[ItemInDB], ItemRepository):
    def __init__(self, connection_manager: ConnectionManager):
        super().__init__(connection_manager, self._map_row_to_item)
        self._init_table()

    @staticmethod
    def _map_row_to_item(row: dict) -> ItemInDB:
        return ItemInDB(
            id=row['id'],
            name=row['name'],
            description=row['description']
        )

    def _init_table(self):
        with self._conn_mgr.transaction() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS items (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(255) NOT NULL,
                        description TEXT NOT NULL
                    )
                """)

    def create(self, item: Item) -> ItemInDB:
        with self._conn_mgr.transaction() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    "INSERT INTO items (name, description) VALUES (%s, %s) RETURNING id, name, description",
                    (item.name, item.description)
                )
                row = cur.fetchone()
                if row is None:
                    raise ItemCreationException("Failed to create item")
                return self._row_to_model(row)

    def get_by_id(self, item_id: int) -> Optional[ItemInDB]:
        with self._conn_mgr.query() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    "SELECT id, name, description FROM items WHERE id = %s",
                    (item_id,)
                )
                row = cur.fetchone()
            if row is None:
                return None
            return self._row_to_model(row)

    def get_all(self) -> list[ItemInDB]:
        with self._conn_mgr.query() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT id, name, description FROM items ORDER BY id")
                rows = cur.fetchall()
            return [self._row_to_model(row) for row in rows]

    def update(self, item_id: int, item: Item) -> Optional[ItemInDB]:
        with self._conn_mgr.transaction() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    "UPDATE items SET name = %s, description = %s WHERE id = %s RETURNING id, name, description",
                    (item.name, item.description, item_id)
                )
                row = cur.fetchone()
            if row is None:
                return None
            return self._row_to_model(row)

    def delete(self, item_id: int) -> bool:
        with self._conn_mgr.transaction() as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM items WHERE id = %s", (item_id,))
                deleted = cur.rowcount > 0
            return deleted
