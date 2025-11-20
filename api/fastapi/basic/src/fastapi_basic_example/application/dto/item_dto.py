"""Item DTOs."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class ItemResponseDTO:
    """Item response DTO."""

    item_id: int
    q: Optional[str] = None


@dataclass
class HealthCheckDTO:
    """Health check response DTO."""

    status: str = "healthy"


@dataclass
class WelcomeDTO:
    """Welcome message DTO."""

    Hello: str = "World"
