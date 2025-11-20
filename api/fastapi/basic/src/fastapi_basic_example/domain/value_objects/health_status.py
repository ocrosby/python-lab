"""Health status constants."""

from enum import Enum


class HealthStatus(str, Enum):
    """Health status constants."""

    HEALTHY = "healthy"
    READY = "ready"
    ALIVE = "alive"
    STARTED = "started"
