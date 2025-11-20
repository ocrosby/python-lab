"""FastAPI application entry point."""

import os

from fastapi import FastAPI

from .domain.constants import AppConstants
from .infrastructure.di.container import Container
from .infrastructure.logging.config import configure_logging
from .infrastructure.logging.middleware import RequestLoggingMiddleware
from .infrastructure.web.routers import router


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    log_level = os.getenv("LOG_LEVEL", "INFO")
    use_json_logging = os.getenv("JSON_LOGGING", "false").lower() == "true"
    configure_logging(log_level=log_level, use_json=use_json_logging)

    container = Container()
    container.wire(
        modules=[
            "src.fastapi_basic_example.infrastructure.web.routers",
            "src.fastapi_basic_example.main",
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
