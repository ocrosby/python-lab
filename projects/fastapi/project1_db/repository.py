from abc import ABC, abstractmethod
from typing import Optional
import psycopg2
from psycopg2.extras import RealDictCursor

from models import Item, ItemInDB


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


class PostgresItemRepository(ItemRepository):
    def __init__(self, connection_string: str):
        self._connection_string = connection_string
        self._init_table()

    def _get_connection(self):
        return psycopg2.connect(self._connection_string)

    def _init_table(self):
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS items (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(255) NOT NULL,
                        description TEXT NOT NULL
                    )
                """)
            conn.commit()

    def create(self, item: Item) -> ItemInDB:
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    "INSERT INTO items (name, description) VALUES (%s, %s) RETURNING id, name, description",
                    (item.name, item.description)
                )
                row = cur.fetchone()
            conn.commit()
        return ItemInDB(**row)

    def get_by_id(self, item_id: int) -> Optional[ItemInDB]:
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    "SELECT id, name, description FROM items WHERE id = %s",
                    (item_id,)
                )
                row = cur.fetchone()
        if row is None:
            return None
        return ItemInDB(**row)

    def get_all(self) -> list[ItemInDB]:
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT id, name, description FROM items ORDER BY id")
                rows = cur.fetchall()
        return [ItemInDB(**row) for row in rows]

    def update(self, item_id: int, item: Item) -> Optional[ItemInDB]:
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    "UPDATE items SET name = %s, description = %s WHERE id = %s RETURNING id, name, description",
                    (item.name, item.description, item_id)
                )
                row = cur.fetchone()
            conn.commit()
        if row is None:
            return None
        return ItemInDB(**row)

    def delete(self, item_id: int) -> bool:
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM items WHERE id = %s", (item_id,))
                deleted = cur.rowcount > 0
            conn.commit()
        return deleted
