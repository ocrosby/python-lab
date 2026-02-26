"""Dependency injection container."""

from dependency_injector import containers, providers

from ...application.services.health_service import HealthService
from ...application.use_cases.get_item_use_case import GetItemUseCase
from ..config.settings import Settings
from ..persistence.in_memory_item_repository import InMemoryItemRepository
from ..utils.id_generator import UuidGenerator
from ..utils.time_provider import SystemTimeProvider


class Container(containers.DeclarativeContainer):
    """Dependency injection container."""

    wiring_config = containers.WiringConfiguration(
        modules=["fastapi_basic_example.infrastructure.web.routers"]
    )

    settings = providers.Singleton(Settings)

    id_generator = providers.Singleton(UuidGenerator)

    time_provider = providers.Singleton(SystemTimeProvider)

    item_repository = providers.Singleton(InMemoryItemRepository)

    health_service = providers.Factory(HealthService)

    get_item_use_case = providers.Factory(
        GetItemUseCase,
        item_repository=item_repository,
    )


container = Container()
