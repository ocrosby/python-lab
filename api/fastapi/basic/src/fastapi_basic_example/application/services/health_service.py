"""Health service for checking application health."""

import structlog

from ...domain.constants import HealthConstants
from ...infrastructure.logging.context import get_logger_context
from ...infrastructure.utils.datetime_utils import current_utc_timestamp
from ..dto.item_dto import HealthCheckDTO

logger = structlog.get_logger(__name__)


class HealthService:
    """Service for health checks."""

    def __init__(self):
        """Initialize the health service."""
        logger.info("Health service initialized", **get_logger_context())

    def get_health_status(self) -> HealthCheckDTO:
        """Get the health status of the application."""
        logger.debug("Health status requested", **get_logger_context())
        return HealthCheckDTO(
            status=HealthConstants.HEALTHY, timestamp=current_utc_timestamp()
        )

    async def is_ready(self) -> bool:
        """Check if the application is ready to serve traffic."""
        logger.debug("Readiness check requested", **get_logger_context())
        return True

    async def is_alive(self) -> bool:
        """Check if the application is alive."""
        logger.debug("Liveness check requested", **get_logger_context())
        return True
