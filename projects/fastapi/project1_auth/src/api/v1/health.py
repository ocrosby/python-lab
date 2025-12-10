from fastapi import APIRouter, Depends
from typing import Annotated

from dtos import HealthResponse
from dependencies import get_connection_manager
from repository import ConnectionManager

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/liveness", response_model=HealthResponse)
def liveness():
    return HealthResponse(status="alive")


@router.get("/readiness", response_model=HealthResponse)
async def readiness(
    conn_mgr: Annotated[ConnectionManager, Depends(get_connection_manager)]
):
    try:
        with conn_mgr.query() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
                cur.fetchone()
        return HealthResponse(status="ready")
    except Exception as e:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database connection failed: {str(e)}"
        )


@router.get("/startup", response_model=HealthResponse)
def startup():
    return HealthResponse(status="started")
