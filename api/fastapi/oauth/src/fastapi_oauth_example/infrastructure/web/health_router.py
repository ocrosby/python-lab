from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from fastapi_oauth_example.application.services.health_service import HealthService


class HealthCheckResponse(BaseModel):
    status: str
    timestamp: str
    uptime_seconds: float | None = None


class ProbeResponse(BaseModel):
    status: str


router = APIRouter(tags=["Health"])

_health_service_instance: HealthService | None = None


def get_health_service() -> HealthService:
    global _health_service_instance
    if _health_service_instance is None:
        _health_service_instance = HealthService()
    return _health_service_instance


def create_probe_response(status: str) -> ProbeResponse:
    return ProbeResponse(status=status)


@router.get("/health", response_model=HealthCheckResponse)
async def health_check(
    health_service: Annotated[HealthService, Depends(get_health_service)],
) -> HealthCheckResponse:
    return HealthCheckResponse(
        status="healthy",
        timestamp=datetime.now(UTC).isoformat(),
        uptime_seconds=health_service.get_uptime_seconds(),
    )


@router.get(
    "/health/live",
    response_model=ProbeResponse,
    include_in_schema=True,
    tags=["Probes"],
)
@router.get("/livez", include_in_schema=False)
@router.get("/healthz", include_in_schema=False)
async def liveness_probe(
    health_service: Annotated[HealthService, Depends(get_health_service)],
) -> ProbeResponse:
    if await health_service.is_alive():
        return create_probe_response("alive")
    raise HTTPException(status_code=503, detail="Service not alive")


@router.get(
    "/health/ready",
    response_model=ProbeResponse,
    include_in_schema=True,
    tags=["Probes"],
)
@router.get("/readyz", include_in_schema=False)
@router.get("/readiness", include_in_schema=False)
async def readiness_probe(
    health_service: Annotated[HealthService, Depends(get_health_service)],
) -> ProbeResponse:
    if await health_service.is_ready():
        return create_probe_response("ready")
    raise HTTPException(status_code=503, detail="Service not ready")


@router.get(
    "/health/startup",
    response_model=ProbeResponse,
    include_in_schema=True,
    tags=["Probes"],
)
@router.get("/startupz", include_in_schema=False)
async def startup_probe(
    health_service: Annotated[HealthService, Depends(get_health_service)],
) -> ProbeResponse:
    if await health_service.is_alive():
        return create_probe_response("started")
    raise HTTPException(status_code=503, detail="Service not started")
