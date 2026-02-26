"""API routers for the FastAPI application."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from ...application.dto.item_dto import (
    HealthCheckDTO,
    ItemResponseDTO,
    ProbeResponseDTO,
    WelcomeDTO,
)
from ...application.services.health_service import HealthService
from ...application.use_cases.get_item_use_case import GetItemUseCase
from ...domain.constants import HealthConstants
from ...domain.value_objects.query_params import QueryParams
from ...infrastructure.utils.datetime_utils import current_utc_timestamp
from ..di.dependencies import get_health_service, get_item_use_case

router = APIRouter()


def create_probe_response(status: str) -> ProbeResponseDTO:
    """Create a probe response DTO."""
    return ProbeResponseDTO(
        status=status,
        timestamp=current_utc_timestamp(),
    )


@router.get("/", response_model=WelcomeDTO)
async def read_root(
    health_service: Annotated[HealthService, Depends(get_health_service)],
) -> WelcomeDTO:
    """Root endpoint."""
    return health_service.get_welcome_message()


@router.get("/items/{item_id}", response_model=ItemResponseDTO)
async def read_item(
    item_id: int,
    q: str | None = None,
    *,
    use_case: Annotated[GetItemUseCase, Depends(get_item_use_case)],
) -> ItemResponseDTO:
    """Get item by ID."""
    query_params = QueryParams(q=q) if q is not None else None
    return await use_case.execute(item_id, query_params)


@router.get("/health", response_model=HealthCheckDTO, tags=["Health"])
async def health_check(
    health_service: Annotated[HealthService, Depends(get_health_service)],
) -> HealthCheckDTO:
    """Health check endpoint."""
    return health_service.get_health_status()


@router.get(
    "/health/live",
    response_model=ProbeResponseDTO,
    include_in_schema=True,
    tags=["Probes"],
)
@router.get("/healthz", include_in_schema=False)
async def liveness_probe(
    health_service: Annotated[HealthService, Depends(get_health_service)],
) -> ProbeResponseDTO:
    """Kubernetes liveness probe endpoint.

    This endpoint indicates whether the application is running.
    If it fails, Kubernetes will restart the container.
    """
    if await health_service.is_alive():
        return create_probe_response(HealthConstants.ALIVE)
    raise HTTPException(status_code=503, detail="Service not alive")


@router.get(
    "/health/ready",
    response_model=ProbeResponseDTO,
    include_in_schema=True,
    tags=["Probes"],
)
@router.get("/readiness", include_in_schema=False)
async def readiness_probe(
    health_service: Annotated[HealthService, Depends(get_health_service)],
) -> ProbeResponseDTO:
    """Kubernetes readiness probe endpoint.

    This endpoint indicates whether the application is ready to serve traffic.
    If it fails, Kubernetes will stop sending traffic to this instance.
    """
    if await health_service.is_ready():
        return create_probe_response(HealthConstants.READY)
    raise HTTPException(status_code=503, detail="Service not ready")


@router.get(
    "/health/startup",
    response_model=ProbeResponseDTO,
    include_in_schema=True,
    tags=["Probes"],
)
async def startup_probe(
    health_service: Annotated[HealthService, Depends(get_health_service)],
) -> ProbeResponseDTO:
    """Kubernetes startup probe endpoint.

    This endpoint indicates whether the application has finished starting up.
    If it fails, Kubernetes will restart the container.
    Used for applications with slow startup times.
    """
    if await health_service.is_alive():
        return create_probe_response(HealthConstants.STARTED)
    raise HTTPException(status_code=503, detail="Service not started")
