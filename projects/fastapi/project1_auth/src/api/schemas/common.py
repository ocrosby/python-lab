from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    detail: str = Field(..., description="Error message")
    error_code: Optional[str] = Field(None, description="Error code")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(), description="Error timestamp")


class HealthResponse(BaseModel):
    status: str = Field(..., description="Health status")


class ApiInfoResponse(BaseModel):
    name: str = Field(..., description="API name")
    version: str = Field(..., description="API version")
    description: str = Field(..., description="API description")
    links: list[dict] = Field(..., description="Available endpoints")
