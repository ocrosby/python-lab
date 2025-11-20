"""Item DTOs."""

from pydantic import BaseModel, Field


class ItemResponseDTO(BaseModel):
    """Item response DTO."""

    item_id: int = Field(..., gt=0, description="Item ID must be positive")
    q: str | None = None


class HealthCheckDTO(BaseModel):
    """Health check response DTO."""

    status: str
    timestamp: str


class DetailedHealthCheckDTO(BaseModel):
    """Detailed health check response DTO."""

    status: str
    timestamp: str
    uptime_seconds: float
    version: str


class WelcomeDTO(BaseModel):
    """Welcome message DTO."""

    Hello: str = "World"


class ProbeResponseDTO(BaseModel):
    """Probe response DTO."""

    status: str
    timestamp: str
