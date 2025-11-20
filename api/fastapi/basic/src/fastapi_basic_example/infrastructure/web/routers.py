"""API routers for the FastAPI application."""

from datetime import datetime, timezone
from typing import Optional

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException

from ...application.dto.item_dto import HealthCheckDTO, ItemResponseDTO, WelcomeDTO
from ...application.services.health_service import HealthService
from ...application.use_cases.get_item_use_case import GetItemUseCase
from ...domain.value_objects.query_params import QueryParams
from ..di.container import Container

# Create router
router = APIRouter()


@router.get("/", response_model=WelcomeDTO)
@inject
async def read_root(
    health_service: HealthService = Depends(Provide[Container.health_service]),
) -> WelcomeDTO:
    """Root endpoint."""
    return health_service.get_welcome_message()


@router.get("/items/{item_id}", response_model=ItemResponseDTO)
@inject
async def read_item(
    item_id: int,
    q: Optional[str] = None,
    use_case: GetItemUseCase = Depends(Provide[Container.get_item_use_case]),
) -> ItemResponseDTO:
    """Get item by ID."""
    query_params = QueryParams(q=q) if q is not None else None
    return await use_case.execute(item_id, query_params)


@router.get("/health", response_model=HealthCheckDTO)
@inject
async def health_check(
    health_service: HealthService = Depends(Provide[Container.health_service]),
) -> HealthCheckDTO:
    """Health check endpoint."""
    return health_service.get_health_status()


@router.get("/health/live")
@router.get("/healthz")
@inject
async def liveness_probe(
    health_service: HealthService = Depends(Provide[Container.health_service]),
):
    """Kubernetes liveness probe endpoint.

    This endpoint indicates whether the application is running.
    If it fails, Kubernetes will restart the container.
    """
    if await health_service.is_alive():
        return {"status": "alive", "timestamp": datetime.now(timezone.utc).isoformat()}
    else:
        raise HTTPException(status_code=503, detail="Service not alive")


@router.get("/health/ready")
@router.get("/readiness")
@inject
async def readiness_probe(
    health_service: HealthService = Depends(Provide[Container.health_service]),
):
    """Kubernetes readiness probe endpoint.

    This endpoint indicates whether the application is ready to serve traffic.
    If it fails, Kubernetes will stop sending traffic to this instance.
    """
    if await health_service.is_ready():
        return {"status": "ready", "timestamp": datetime.now(timezone.utc).isoformat()}
    else:
        raise HTTPException(status_code=503, detail="Service not ready")


@router.get("/health/startup")
@inject
async def startup_probe(
    health_service: HealthService = Depends(Provide[Container.health_service]),
):
    """Kubernetes startup probe endpoint.

    This endpoint indicates whether the application has finished starting up.
    If it fails, Kubernetes will restart the container.
    Used for applications with slow startup times.
    """
    if await health_service.is_alive():
        return {
            "status": "started",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    else:
        raise HTTPException(status_code=503, detail="Service not started")
