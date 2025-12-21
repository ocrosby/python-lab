import os
from fastapi import FastAPI, HTTPException, Depends, Request, Response, Header
from typing import Optional

from models import Item, ItemInDB, Link
from repository import PostgresItemRepository, ItemRepository
from service import ItemService, ItemNotFoundException

app = FastAPI(
    title="Project1",
    version="1.0.0",
    contact={
        "name": "Omar Crosby",
        "email": "omar.crosby@gmail.com"
    }
)


def validate_content_type(content_type: Optional[str] = Header(None)):
    if content_type and "application/json" not in content_type:
        raise HTTPException(status_code=415, detail="Unsupported Media Type. Use application/json")


def validate_accept(accept: Optional[str] = Header(None)):
    if accept and accept != "*/*" and "application/json" not in accept:
        raise HTTPException(status_code=406, detail="Not Acceptable. API only supports application/json")

database_url = os.getenv("DATABASE_URL", "postgresql://project1:project1@localhost:5432/project1")
_repository = PostgresItemRepository(database_url)
_service = ItemService(_repository)


def get_item_service() -> ItemService:
    return _service


def create_item_links(item_id: int, request: Request) -> list[Link]:
    base_url = str(request.base_url).rstrip('/')
    return [
        Link(href=f"{base_url}/api/v1/items/{item_id}", rel="self", method="GET"),
        Link(href=f"{base_url}/api/v1/items/{item_id}", rel="update", method="PUT"),
        Link(href=f"{base_url}/api/v1/items/{item_id}", rel="delete", method="DELETE"),
        Link(href=f"{base_url}/api/v1/items", rel="collection", method="GET")
    ]


@app.get("/")
def read_root(request: Request):
    base_url = str(request.base_url).rstrip('/')
    return {
        "name": "Project1 API",
        "version": "1.0.0",
        "description": "RESTful API for managing items",
        "links": [
            {"href": f"{base_url}/api/v1/items", "rel": "items", "method": "GET"},
            {"href": f"{base_url}/api/v1/items", "rel": "create-item", "method": "POST"},
            {"href": f"{base_url}/health/liveness", "rel": "health-liveness", "method": "GET"},
            {"href": f"{base_url}/health/readiness", "rel": "health-readiness", "method": "GET"},
            {"href": f"{base_url}/health/startup", "rel": "health-startup", "method": "GET"}
        ]
    }


@app.post("/api/v1/items", response_model=ItemInDB, status_code=201, tags=["items"], dependencies=[Depends(validate_content_type), Depends(validate_accept)])
def create_item(item: Item, request: Request, response: Response, service: ItemService = Depends(get_item_service)):
    response.headers["Cache-Control"] = "no-cache"
    response.headers["Content-Type"] = "application/json"
    created_item = service.create_item(item)
    created_item.links = create_item_links(created_item.id, request)
    response.headers["Location"] = f"{request.base_url}api/v1/items/{created_item.id}"
    return created_item


@app.get("/api/v1/items", response_model=list[ItemInDB], tags=["items"], dependencies=[Depends(validate_accept)])
def get_items(request: Request, response: Response, service: ItemService = Depends(get_item_service)):
    response.headers["Cache-Control"] = "max-age=60, public"
    response.headers["Content-Type"] = "application/json"
    items = service.get_all_items()
    for item in items:
        item.links = create_item_links(item.id, request)
    return items


@app.get("/api/v1/items/{item_id}", response_model=ItemInDB, tags=["items"], dependencies=[Depends(validate_accept)])
def get_item(item_id: int, request: Request, response: Response, service: ItemService = Depends(get_item_service)):
    response.headers["Cache-Control"] = "max-age=60, public"
    response.headers["Content-Type"] = "application/json"
    try:
        item = service.get_item(item_id)
        item.links = create_item_links(item.id, request)
        return item
    except ItemNotFoundException:
        raise HTTPException(status_code=404, detail="Item not found")


@app.put("/api/v1/items/{item_id}", response_model=ItemInDB, tags=["items"], dependencies=[Depends(validate_content_type), Depends(validate_accept)])
def update_item(item_id: int, item: Item, request: Request, response: Response, service: ItemService = Depends(get_item_service)):
    response.headers["Cache-Control"] = "no-cache"
    response.headers["Content-Type"] = "application/json"
    try:
        updated_item = service.update_item(item_id, item)
        updated_item.links = create_item_links(updated_item.id, request)
        return updated_item
    except ItemNotFoundException:
        raise HTTPException(status_code=404, detail="Item not found")


@app.delete("/api/v1/items/{item_id}", response_model=ItemInDB, status_code=200, tags=["items"], dependencies=[Depends(validate_accept)])
def delete_item(item_id: int, request: Request, response: Response, service: ItemService = Depends(get_item_service)):
    response.headers["Cache-Control"] = "no-cache"
    response.headers["Content-Type"] = "application/json"
    try:
        item = service.get_item(item_id)
        item.links = create_item_links(item.id, request)
        service.delete_item(item_id)
        return item
    except ItemNotFoundException:
        raise HTTPException(status_code=404, detail="Item not found")


@app.get("/health/liveness", tags=["health"])
def liveness():
    return {"status": "alive"}


@app.get("/health/readiness", tags=["health"])
def readiness():
    return {"status": "ready"}


@app.get("/health/startup", tags=["health"])
def startup():
    return {"status": "started"}
