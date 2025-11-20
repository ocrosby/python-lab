"""FastAPI application entry point."""

import os

from fastapi import FastAPI

from .infrastructure.di.container import Container
from .infrastructure.logging.config import configure_logging
from .infrastructure.logging.middleware import RequestLoggingMiddleware
from .infrastructure.web.routers import router

# Constants to eliminate duplication
APP_NAME = "FastAPI Basic Example"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = (
    "A FastAPI application demonstrating hexagonal architecture "
    "with DI and structured logging"
)


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
            "src.fastapi_basic_example.infrastructure.web.routers",
            "src.fastapi_basic_example.main",
        ]
    )

    # Create FastAPI app
    app = FastAPI(
        title=APP_NAME,
        description=APP_DESCRIPTION,
        version=APP_VERSION,
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
