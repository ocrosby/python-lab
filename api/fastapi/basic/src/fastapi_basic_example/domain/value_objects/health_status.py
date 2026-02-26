"""Health status value object."""

from dataclasses import dataclass


@dataclass(frozen=True)
class HealthStatus:
    """Value object for health status."""

    value: str

    @classmethod
    def healthy(cls) -> "HealthStatus":
        """Create healthy status."""
        return cls("healthy")

    @classmethod
    def unhealthy(cls) -> "HealthStatus":
        """Create unhealthy status."""
        return cls("unhealthy")

    @classmethod
    def ready(cls) -> "HealthStatus":
        """Create ready status."""
        return cls("ready")

    @classmethod
    def alive(cls) -> "HealthStatus":
        """Create alive status."""
        return cls("alive")

    @classmethod
    def started(cls) -> "HealthStatus":
        """Create started status."""
        return cls("started")

    def __str__(self) -> str:
        """Convert to string."""
        return self.value
