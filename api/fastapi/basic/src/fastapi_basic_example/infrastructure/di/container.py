"""Dependency injection container."""

from dependency_injector import containers, providers

from ...application.services.health_service import HealthService
from ...application.use_cases.get_item_use_case import GetItemUseCase
from ..persistence.in_memory_item_repository import InMemoryItemRepository


class Container(containers.DeclarativeContainer):
    """Dependency injection container."""

    # Configuration
    wiring_config = containers.WiringConfiguration(
        modules=[
            "fastapi_basic_example.infrastructure.web.routers",
            "fastapi_basic_example.main",
        ]
    )

    # Repositories
    item_repository = providers.Singleton(InMemoryItemRepository)

    # Services
    health_service = providers.Factory(HealthService)

    # Use cases
    get_item_use_case = providers.Factory(
        GetItemUseCase,
        repository=item_repository,
    )
