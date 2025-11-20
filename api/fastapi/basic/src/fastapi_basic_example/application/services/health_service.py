"""Health service for checking application health."""

from datetime import UTC, datetime

import structlog

from ...infrastructure.logging.context import get_logger_context
from ..dto.item_dto import HealthCheckDTO, WelcomeDTO

logger = structlog.get_logger(__name__)

# Constants to eliminate duplication
HEALTHY_STATUS = "healthy"
APP_VERSION = "1.0.0"


def get_current_timestamp() -> str:
    """Get current UTC timestamp in ISO format."""
    return datetime.now(UTC).isoformat()


def get_current_datetime() -> datetime:
    """Get current UTC datetime."""
    return datetime.now(UTC)


class HealthService:
    """Service for health checks."""

    def __init__(self):
        """Initialize the health service."""
        self.startup_time = get_current_datetime()
        logger.info("Health service initialized", **get_logger_context())

    def get_health_status(self) -> HealthCheckDTO:
        """Get the health status of the application."""
        logger.debug("Health status requested", **get_logger_context())
        return HealthCheckDTO()

    def get_welcome_message(self) -> WelcomeDTO:
        """Get welcome message."""
        logger.debug("Welcome message requested", **get_logger_context())
        return WelcomeDTO()

    async def get_detailed_health_status(self):
        """Get detailed health status of the application."""
        uptime_seconds = (get_current_datetime() - self.startup_time).total_seconds()

        status = {
            "status": HEALTHY_STATUS,
            "timestamp": get_current_timestamp(),
            "uptime_seconds": uptime_seconds,
            "version": APP_VERSION,
        }

        logger.info(
            "Detailed health status requested",
            uptime_seconds=uptime_seconds,
            **get_logger_context(),
        )

        return status

    async def is_ready(self):
        """Check if the application is ready to serve traffic."""
        # Add any dependency checks here (database, external services, etc.)
        logger.debug("Readiness check requested", **get_logger_context())
        return True

    async def is_alive(self):
        """Check if the application is alive."""
        logger.debug("Liveness check requested", **get_logger_context())
        return True
