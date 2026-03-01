import logging
from datetime import UTC, datetime

logger = logging.getLogger(__name__)


class HealthService:

    def __init__(self):
        self.startup_time = datetime.now(UTC)
        logger.info("Health service initialized")

    async def is_ready(self) -> bool:
        logger.debug("Readiness check requested")
        return True

    async def is_alive(self) -> bool:
        logger.debug("Liveness check requested")
        return True

    def get_uptime_seconds(self) -> float:
        return (datetime.now(UTC) - self.startup_time).total_seconds()
