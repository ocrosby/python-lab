from abc import ABC, abstractmethod
from typing import Protocol, Optional, Tuple
from models import Item, ItemInDB, UserCreate, UserInDB


class IItemService(Protocol):
    def create_item(self, item: Item) -> ItemInDB:
        ...
    
    def get_item(self, item_id: int) -> ItemInDB:
        ...
    
    def get_all_items(self) -> list[ItemInDB]:
        ...
    
    def update_item(self, item_id: int, item: Item) -> ItemInDB:
        ...
    
    def delete_item(self, item_id: int) -> None:
        ...


class IAuthService(Protocol):
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        ...
    
    def get_password_hash(self, password: str) -> str:
        ...
    
    def authenticate_user(self, username: str, password: str) -> Optional[UserInDB]:
        ...
    
    def create_access_token(self, data: dict, expires_delta: Optional[object] = None) -> str:
        ...
    
    def decode_token(self, token: str) -> object:
        ...
    
    def register_user(self, user: UserCreate) -> UserInDB:
        ...
    
    def get_user_by_username(self, username: str) -> Optional[UserInDB]:
        ...
    
    def create_refresh_token(self, user_id: int, token_family: Optional[str] = None) -> str:
        ...
    
    def create_token_pair(self, user: UserInDB) -> Tuple[str, str, str]:
        ...
    
    def refresh_access_token(self, refresh_token: str) -> Tuple[str, str]:
        ...
    
    def revoke_refresh_token(self, refresh_token: str) -> bool:
        ...
    
    def revoke_all_user_tokens(self, user_id: int) -> int:
        ...


class ILogger(Protocol):
    def debug(self, message: str, **kwargs) -> None:
        ...
    
    def info(self, message: str, **kwargs) -> None:
        ...
    
    def warning(self, message: str, **kwargs) -> None:
        ...
    
    def error(self, message: str, **kwargs) -> None:
        ...
    
    def critical(self, message: str, **kwargs) -> None:
        ...
