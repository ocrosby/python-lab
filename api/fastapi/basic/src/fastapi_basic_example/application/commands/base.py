"""Base command pattern interfaces."""

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from ...domain.result import Result

TRequest = TypeVar("TRequest")
TResponse = TypeVar("TResponse")
TError = TypeVar("TError")


class Command(ABC, Generic[TRequest, TResponse, TError]):
    """Base command interface for CQRS pattern."""

    @abstractmethod
    async def execute(self, request: TRequest) -> Result[TResponse, TError]:
        """Execute the command with the given request."""
        pass


class Query(ABC, Generic[TRequest, TResponse, TError]):
    """Base query interface for CQRS pattern."""

    @abstractmethod
    async def execute(self, request: TRequest) -> Result[TResponse, TError]:
        """Execute the query with the given request."""
        pass
