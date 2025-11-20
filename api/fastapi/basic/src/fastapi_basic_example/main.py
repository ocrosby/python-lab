"""FastAPI application entry point."""

from fastapi import FastAPI

from .domain.constants import AppConstants
from .infrastructure.config.settings import settings
from .infrastructure.di.container import Container
from .infrastructure.logging.config import configure_logging
from .infrastructure.logging.middleware import RequestLoggingMiddleware
from .infrastructure.web.routers import router


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    configure_logging(log_level=settings.log_level, use_json=settings.json_logging)

    container = Container()
    container.wire(
        modules=[
            "fastapi_basic_example.infrastructure.web.routers",
            "fastapi_basic_example.main",
        ]
    )

    app = FastAPI(
        title=AppConstants.NAME,
        description=AppConstants.DESCRIPTION,
        version=AppConstants.VERSION,
    )

    app.container = container

    app.add_middleware(RequestLoggingMiddleware)

    app.include_router(router)

    return app


app = create_app()
