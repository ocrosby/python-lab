from abc import ABC
from typing import TypeVar, Generic, Callable
from contextlib import contextmanager
from psycopg2 import pool


T = TypeVar('T')


class RepositoryException(Exception):
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
