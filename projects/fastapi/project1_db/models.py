from typing import Optional
from pydantic import BaseModel


class Item(BaseModel):
    name: str
    description: str


class Link(BaseModel):
    href: str
    rel: str
    method: str = "GET"


class ItemInDB(BaseModel):
    id: int
    name: str
    description: str
    links: Optional[list[Link]] = None
