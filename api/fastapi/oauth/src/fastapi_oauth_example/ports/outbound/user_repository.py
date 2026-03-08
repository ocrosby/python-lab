from abc import ABC, abstractmethod

from fastapi_oauth_example.domain.entities.user import User
from fastapi_oauth_example.domain.value_objects.email import Email
from fastapi_oauth_example.domain.value_objects.user_id import UserId


class UserRepository(ABC):
    @abstractmethod
    async def create(self, user: User) -> User:
        pass

    @abstractmethod
    async def get_by_id(self, user_id: UserId) -> User | None:
        pass

    @abstractmethod
    async def get_by_email(self, email: Email) -> User | None:
        pass

    @abstractmethod
    async def get_by_username(self, username: str) -> User | None:
        pass

    @abstractmethod
    async def update(self, user: User) -> User:
        pass

    @abstractmethod
    async def delete(self, user_id: UserId) -> bool:
        pass

    @abstractmethod
    async def exists_by_email(self, email: Email) -> bool:
        pass

    @abstractmethod
    async def exists_by_username(self, username: str) -> bool:
        pass
