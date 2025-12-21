from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional
from datetime import datetime


class UserCreateRequest(BaseModel):
    email: EmailStr = Field(..., description="User email address")
    username: str = Field(..., min_length=3, max_length=50, description="Username")
    password: str = Field(..., min_length=8, max_length=72, description="Password")


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int = Field(..., description="User ID")
    email: str = Field(..., description="User email address")
    username: str = Field(..., description="Username")
    is_active: bool = Field(..., description="Whether user is active")


class TokenResponse(BaseModel):
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")


class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(..., description="Refresh token to exchange")


class ItemCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Item name")
    description: str = Field(..., min_length=1, description="Item description")


class ItemUpdateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Item name")
    description: str = Field(..., min_length=1, description="Item description")


class LinkResponse(BaseModel):
    href: str = Field(..., description="Link URL")
    rel: str = Field(..., description="Link relationship")
    method: str = Field(default="GET", description="HTTP method")


class ItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int = Field(..., description="Item ID")
    name: str = Field(..., description="Item name")
    description: str = Field(..., description="Item description")
    links: Optional[list[LinkResponse]] = Field(None, description="HATEOAS links")


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
