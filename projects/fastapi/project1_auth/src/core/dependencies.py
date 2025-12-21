from functools import lru_cache
from typing import Annotated, Optional
from contextlib import asynccontextmanager
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from psycopg2 import pool

from settings import Settings, get_settings
from repository import PostgresItemRepository, PostgresUserRepository, PostgresRefreshTokenRepository, ConnectionManager
from service import ItemService
from auth_service import AuthService, AuthenticationException
from models import User

_connection_pool: Optional[pool.SimpleConnectionPool] = None
_connection_manager: Optional[ConnectionManager] = None

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/token")


@asynccontextmanager
async def lifespan_context(app):
    import asyncio
    from tasks import cleanup_expired_refresh_tokens
    
    global _connection_pool, _connection_manager
    settings = get_settings()
    _connection_pool = pool.SimpleConnectionPool(
        settings.db_pool_min_conn,
        settings.db_pool_max_conn,
        settings.database_url
    )
    _connection_manager = ConnectionManager(_connection_pool)
    
    async def periodic_cleanup():
        while True:
            await asyncio.sleep(3600)
            if _connection_manager is not None:
                token_repo = PostgresRefreshTokenRepository(_connection_manager)
                await asyncio.to_thread(cleanup_expired_refresh_tokens, token_repo)
    
    cleanup_task = asyncio.create_task(periodic_cleanup())
    
    yield
    
    cleanup_task.cancel()
    try:
        await cleanup_task
    except asyncio.CancelledError:
        pass
    
    if _connection_pool:
        _connection_pool.closeall()


@lru_cache
def get_cached_settings() -> Settings:
    return get_settings()


def get_connection_pool() -> pool.SimpleConnectionPool:
    if _connection_pool is None:
        raise RuntimeError("Connection pool not initialized")
    return _connection_pool


def get_connection_manager() -> ConnectionManager:
    if _connection_manager is None:
        raise RuntimeError("Connection manager not initialized")
    return _connection_manager


def get_item_service(
    conn_mgr: Annotated[ConnectionManager, Depends(get_connection_manager)]
) -> ItemService:
    item_repository = PostgresItemRepository(conn_mgr)
    return ItemService(item_repository)


def get_auth_service(
    settings: Annotated[Settings, Depends(get_cached_settings)],
    conn_mgr: Annotated[ConnectionManager, Depends(get_connection_manager)]
) -> AuthService:
    user_repository = PostgresUserRepository(conn_mgr)
    refresh_token_repository = PostgresRefreshTokenRepository(conn_mgr)
    return AuthService(
        user_repository,
        refresh_token_repository,
        settings.secret_key,
        settings.algorithm,
        settings.access_token_expire_minutes,
        settings.refresh_token_expire_days
    )


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)]
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        token_data = auth_service.decode_token(token)
        if token_data.username is None:
            raise credentials_exception
        user = auth_service.get_user_by_username(token_data.username)
        if user is None:
            raise credentials_exception
    except AuthenticationException:
        raise credentials_exception
    return User(id=user.id, email=user.email, username=user.username, is_active=user.is_active)


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)]
) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
