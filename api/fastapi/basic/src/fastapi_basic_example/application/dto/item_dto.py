"""Item DTOs."""

from dataclasses import dataclass


@dataclass
class ItemResponseDTO:
    """Item response DTO."""

    item_id: int
    q: str | None = None


@dataclass
class HealthCheckDTO:
    """Health check response DTO."""

    status: str = "healthy"


@dataclass
class WelcomeDTO:
    """Welcome message DTO."""

    Hello: str = "World"
