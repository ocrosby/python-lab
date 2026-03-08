"""FastAPI dependency injection functions."""

from typing import Annotated

from fastapi import Depends

from ...adapters.outbound.persistence.in_memory_item_repository import (
    InMemoryItemRepository,
)
from ...application.services.health_service import HealthService
from ...application.use_cases.get_item_use_case import GetItemUseCase
from ...ports.outbound.item_repository import ItemRepository
from ..utils.id_generator import IdGenerator, UuidGenerator
from ..utils.time_provider import SystemTimeProvider, TimeProvider


def get_id_generator() -> IdGenerator:
    """Get ID generator instance."""
    return UuidGenerator()


def get_time_provider() -> TimeProvider:
    """Get time provider instance."""
    return SystemTimeProvider()


def get_item_repository() -> ItemRepository:
    """Get item repository instance."""
    return InMemoryItemRepository()


def get_health_service() -> HealthService:
    """Get health service instance."""
    return HealthService()


def get_item_use_case(
    repository: Annotated[ItemRepository, Depends(get_item_repository)],
) -> GetItemUseCase:
    """Get item use case instance."""
    return GetItemUseCase(item_repository=repository)
