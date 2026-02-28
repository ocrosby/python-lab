"""FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from .domain.constants import AppConstants
from .infrastructure.config.settings import Settings
from .infrastructure.di.dependencies import get_id_generator, get_time_provider
from .infrastructure.logging.config import configure_logging
from .infrastructure.logging.middleware import (
    RequestIDMiddleware,
    RequestLoggingMiddleware,
    TimingMiddleware,
)
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

    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.allowed_hosts,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=settings.cors_allow_credentials,
        allow_methods=settings.cors_allow_methods,
        allow_headers=settings.cors_allow_headers,
    )

    app.add_middleware(
        GZipMiddleware,
        minimum_size=settings.gzip_minimum_size,
        compresslevel=settings.gzip_compression_level,
    )

    app.add_middleware(TimingMiddleware, time_provider=get_time_provider())
    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(RequestIDMiddleware, id_generator=get_id_generator())

    app.include_router(router)

    return app
