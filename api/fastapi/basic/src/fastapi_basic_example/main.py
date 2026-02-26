"""FastAPI application entry point."""

from fastapi import FastAPI

from .domain.constants import AppConstants
from .infrastructure.config.settings import Settings
from .infrastructure.di.dependencies import get_id_generator, get_time_provider
from .infrastructure.logging.config import configure_logging
from .infrastructure.logging.middleware import RequestLoggingMiddleware
from .infrastructure.web.routers import router


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = Settings()
    configure_logging(log_level=settings.log_level, use_json=settings.json_logging)

    app = FastAPI(
        title=AppConstants.NAME,
        description=AppConstants.DESCRIPTION,
        version=AppConstants.VERSION,
    )

    id_generator = get_id_generator()
    time_provider = get_time_provider()
    app.add_middleware(
        RequestLoggingMiddleware,
        id_generator=id_generator,
        time_provider=time_provider,
    )

    app.include_router(router)

    return app
