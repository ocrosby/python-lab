"""FastAPI application entry point."""

import os

from fastapi import FastAPI

from .infrastructure.di.container import Container
from .infrastructure.logging.config import configure_logging
from .infrastructure.logging.middleware import RequestLoggingMiddleware
from .infrastructure.web.routers import router


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    # Configure logging
    log_level = os.getenv("LOG_LEVEL", "INFO")
    use_json_logging = os.getenv("JSON_LOGGING", "false").lower() == "true"
    configure_logging(log_level=log_level, use_json=use_json_logging)

    # Initialize DI container
    container = Container()
    container.wire(
        modules=[
            "fastapi_basic_example.infrastructure.web.routers",
            "fastapi_basic_example.main",
        ]
    )

    # Create FastAPI app
    app = FastAPI(
        title="FastAPI Basic Example",
        description=(
            "A FastAPI application demonstrating hexagonal architecture "
            "with DI and structured logging"
        ),
        version="1.0.0",
    )

    # Add container to app state for testing access
    app.container = container

    # Add middleware
    app.add_middleware(RequestLoggingMiddleware)

    # Include routers
    app.include_router(router)

    return app


# Create the app instance
app = create_app()
