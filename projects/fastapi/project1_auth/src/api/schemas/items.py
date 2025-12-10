from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


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
