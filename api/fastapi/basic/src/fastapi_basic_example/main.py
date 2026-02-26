"""FastAPI application entry point."""

from fastapi import FastAPI

from .domain.constants import AppConstants
from .infrastructure.di.container import Container
from .infrastructure.logging.config import configure_logging
from .infrastructure.logging.middleware import RequestLoggingMiddleware


def create_app(container: Container | None = None) -> FastAPI:
    """Create and configure the FastAPI application."""
    if container is None:
        container = Container()
        container.wire(modules=["fastapi_basic_example.infrastructure.web.routers"])

    settings = container.settings()
    configure_logging(log_level=settings.log_level, use_json=settings.json_logging)

    from .infrastructure.web.routers import router

    app = FastAPI(
        title=AppConstants.NAME,
        description=AppConstants.DESCRIPTION,
        version=AppConstants.VERSION,
    )

    app.state.container = container

    id_generator = container.id_generator()
    time_provider = container.time_provider()
    app.add_middleware(
        RequestLoggingMiddleware,
        id_generator=id_generator,
        time_provider=time_provider,
    )

    app.include_router(router)

    return app
