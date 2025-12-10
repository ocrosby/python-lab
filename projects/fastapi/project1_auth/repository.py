from abc import ABC, abstractmethod
from typing import Optional, TypeVar, Generic, Callable
from contextlib import contextmanager
from datetime import datetime
import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor

from models import Item, ItemInDB, UserCreate, UserInDB, RefreshTokenInDB

T = TypeVar('T')


class RepositoryException(Exception):
    pass


class ItemCreationException(RepositoryException):
    pass


class UserCreationException(RepositoryException):
    pass


class ConnectionManager:
    def __init__(self, connection_pool: pool.SimpleConnectionPool):
        self._pool = connection_pool

    def get_connection(self):
        return self._pool.getconn()
    
    def return_connection(self, conn):
        self._pool.putconn(conn)

    @contextmanager
    def transaction(self):
        conn = self.get_connection()
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            self.return_connection(conn)

    @contextmanager
    def query(self):
        conn = self.get_connection()
        try:
            yield conn
        finally:
            self.return_connection(conn)


class BaseRepository(ABC, Generic[T]):
    def __init__(self, connection_manager: ConnectionManager, mapper: Callable[[dict], T]):
        self._conn_mgr = connection_manager
        self._mapper = mapper
    
    def _row_to_model(self, row: dict) -> T:
        return self._mapper(row)


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


class UserRepository(ABC):
    @abstractmethod
    def create(self, user: UserCreate, hashed_password: str) -> UserInDB:
        pass

    @abstractmethod
    def get_by_username(self, username: str) -> Optional[UserInDB]:
        pass

    @abstractmethod
    def get_by_email(self, email: str) -> Optional[UserInDB]:
        pass

    @abstractmethod
    def get_by_id(self, user_id: int) -> Optional[UserInDB]:
        pass


class PostgresUserRepository(BaseRepository[UserInDB], UserRepository):
    def __init__(self, connection_manager: ConnectionManager):
        super().__init__(connection_manager, self._map_row_to_user)
        self._init_table()

    @staticmethod
    def _map_row_to_user(row: dict) -> UserInDB:
        return UserInDB(
            id=row['id'],
            email=row['email'],
            username=row['username'],
            hashed_password=row['hashed_password'],
            is_active=row['is_active']
        )

    def _init_table(self):
        with self._conn_mgr.transaction() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        id SERIAL PRIMARY KEY,
                        email VARCHAR(255) UNIQUE NOT NULL,
                        username VARCHAR(255) UNIQUE NOT NULL,
                        hashed_password VARCHAR(255) NOT NULL,
                        is_active BOOLEAN DEFAULT TRUE
                    )
                """)
                cur.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_users_is_active ON users(is_active)")

    def create(self, user: UserCreate, hashed_password: str) -> UserInDB:
        with self._conn_mgr.transaction() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    "INSERT INTO users (email, username, hashed_password) VALUES (%s, %s, %s) RETURNING id, email, username, hashed_password, is_active",
                    (user.email, user.username, hashed_password)
                )
                row = cur.fetchone()
                if row is None:
                    raise UserCreationException("Failed to create user")
                return self._row_to_model(row)

    def get_by_username(self, username: str) -> Optional[UserInDB]:
        with self._conn_mgr.query() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    "SELECT id, email, username, hashed_password, is_active FROM users WHERE username = %s",
                    (username,)
                )
                row = cur.fetchone()
            if row is None:
                return None
            return self._row_to_model(row)

    def get_by_email(self, email: str) -> Optional[UserInDB]:
        with self._conn_mgr.query() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    "SELECT id, email, username, hashed_password, is_active FROM users WHERE email = %s",
                    (email,)
                )
                row = cur.fetchone()
            if row is None:
                return None
            return self._row_to_model(row)

    def get_by_id(self, user_id: int) -> Optional[UserInDB]:
        with self._conn_mgr.query() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    "SELECT id, email, username, hashed_password, is_active FROM users WHERE id = %s",
                    (user_id,)
                )
                row = cur.fetchone()
            if row is None:
                return None
            return self._row_to_model(row)


class RefreshTokenRepository(ABC):
    @abstractmethod
    def create(self, user_id: int, token: str, token_family: str, expires_at: datetime) -> RefreshTokenInDB:
        pass

    @abstractmethod
    def get_by_token(self, token: str) -> Optional[RefreshTokenInDB]:
        pass

    @abstractmethod
    def revoke_by_token(self, token: str) -> bool:
        pass

    @abstractmethod
    def revoke_all_for_user(self, user_id: int) -> int:
        pass

    @abstractmethod
    def revoke_family(self, token_family: str) -> int:
        pass

    @abstractmethod
    def delete_expired(self) -> int:
        pass


class PostgresRefreshTokenRepository(BaseRepository[RefreshTokenInDB], RefreshTokenRepository):
    def __init__(self, connection_manager: ConnectionManager):
        super().__init__(connection_manager, self._map_row_to_refresh_token)
        self._init_table()

    @staticmethod
    def _map_row_to_refresh_token(row: dict) -> RefreshTokenInDB:
        return RefreshTokenInDB(
            id=row['id'],
            user_id=row['user_id'],
            token=row['token'],
            token_family=row['token_family'],
            expires_at=row['expires_at'],
            created_at=row['created_at'],
            revoked=row['revoked']
        )

    def _init_table(self):
        with self._conn_mgr.transaction() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS refresh_tokens (
                        id SERIAL PRIMARY KEY,
                        user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                        token VARCHAR(512) UNIQUE NOT NULL,
                        token_family VARCHAR(64) NOT NULL,
                        expires_at TIMESTAMP NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        revoked BOOLEAN DEFAULT FALSE
                    )
                """)
                cur.execute("CREATE INDEX IF NOT EXISTS idx_token ON refresh_tokens(token)")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_user_id ON refresh_tokens(user_id)")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_token_family ON refresh_tokens(token_family)")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_refresh_tokens_user_revoked ON refresh_tokens(user_id, revoked)")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_refresh_tokens_expires_at ON refresh_tokens(expires_at) WHERE NOT revoked")

    def create(self, user_id: int, token: str, token_family: str, expires_at: datetime) -> RefreshTokenInDB:
        with self._conn_mgr.transaction() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    """INSERT INTO refresh_tokens (user_id, token, token_family, expires_at) 
                       VALUES (%s, %s, %s, %s) 
                       RETURNING id, user_id, token, token_family, expires_at, created_at, revoked""",
                    (user_id, token, token_family, expires_at)
                )
                row = cur.fetchone()
                if row is None:
                    raise RepositoryException("Failed to create refresh token")
                return self._row_to_model(row)

    def get_by_token(self, token: str) -> Optional[RefreshTokenInDB]:
        with self._conn_mgr.query() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    """SELECT id, user_id, token, token_family, expires_at, created_at, revoked 
                       FROM refresh_tokens WHERE token = %s""",
                    (token,)
                )
                row = cur.fetchone()
            if row is None:
                return None
            return self._row_to_model(row)

    def revoke_by_token(self, token: str) -> bool:
        with self._conn_mgr.transaction() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE refresh_tokens SET revoked = TRUE WHERE token = %s",
                    (token,)
                )
                return cur.rowcount > 0

    def revoke_all_for_user(self, user_id: int) -> int:
        with self._conn_mgr.transaction() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE refresh_tokens SET revoked = TRUE WHERE user_id = %s AND revoked = FALSE",
                    (user_id,)
                )
                return cur.rowcount

    def revoke_family(self, token_family: str) -> int:
        with self._conn_mgr.transaction() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE refresh_tokens SET revoked = TRUE WHERE token_family = %s AND revoked = FALSE",
                    (token_family,)
                )
                return cur.rowcount

    def delete_expired(self) -> int:
        with self._conn_mgr.transaction() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "DELETE FROM refresh_tokens WHERE expires_at < CURRENT_TIMESTAMP"
                )
                return cur.rowcount
