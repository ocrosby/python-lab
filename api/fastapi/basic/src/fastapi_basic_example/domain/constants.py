"""Application constants."""


class AppConstants:
    """Application-wide constants."""

    VERSION = "1.0.0"
    NAME = "FastAPI Basic Example"
    DESCRIPTION = (
        "A FastAPI application demonstrating hexagonal architecture "
        "with DI and structured logging"
    )


class HealthConstants:
    """Health check constants."""

    HEALTHY = "healthy"
    READY = "ready"
    ALIVE = "alive"
    STARTED = "started"


class ServerConstants:
    """Server configuration constants."""

    DEFAULT_HOST = "0.0.0.0"
    DEFAULT_PORT = 8000
