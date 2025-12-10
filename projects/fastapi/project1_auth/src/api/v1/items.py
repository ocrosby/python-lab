from fastapi import APIRouter, Depends, Request, Response, Header, status
from typing import Annotated, Optional

from dtos import ItemCreateRequest, ItemUpdateRequest, ItemResponse, LinkResponse
from models import Item, ItemInDB, Link, User
from service import ItemService, ItemNotFoundException
from response_helpers import set_no_cache_headers, set_cache_headers
from dependencies import get_item_service, get_current_active_user

router = APIRouter(prefix="/api/v1/items", tags=["items"])


def validate_content_type(content_type: Optional[str] = Header(None)):
    from fastapi import HTTPException
    if content_type and "application/json" not in content_type:
        raise HTTPException(status_code=415, detail="Unsupported Media Type. Use application/json")


def validate_accept(accept: Optional[str] = Header(None)):
    from fastapi import HTTPException
    if accept and accept != "*/*" and "application/json" not in accept:
        raise HTTPException(status_code=406, detail="Not Acceptable. API only supports application/json")


def create_item_links(item_id: int, request: Request) -> list[LinkResponse]:
    base_url = str(request.base_url).rstrip('/')
    return [
        LinkResponse(href=f"{base_url}/api/v1/items/{item_id}", rel="self", method="GET"),
        LinkResponse(href=f"{base_url}/api/v1/items/{item_id}", rel="update", method="PUT"),
        LinkResponse(href=f"{base_url}/api/v1/items/{item_id}", rel="delete", method="DELETE"),
        LinkResponse(href=f"{base_url}/api/v1/items", rel="collection", method="GET")
    ]


@router.post("", response_model=ItemResponse, status_code=201, dependencies=[Depends(validate_content_type), Depends(validate_accept)])
def create_item(
    item: ItemCreateRequest,
    request: Request,
    response: Response,
    current_user: Annotated[User, Depends(get_current_active_user)],
    service: ItemService = Depends(get_item_service)
):
    set_no_cache_headers(response)
    item_model = Item(name=item.name, description=item.description)
    created_item = service.create_item(item_model)
    links = create_item_links(created_item.id, request)
    response.headers["Location"] = f"{request.base_url}api/v1/items/{created_item.id}"
    return ItemResponse(
        id=created_item.id,
        name=created_item.name,
        description=created_item.description,
        links=links
    )


@router.get("", response_model=list[ItemResponse], dependencies=[Depends(validate_accept)])
def get_items(
    request: Request,
    response: Response,
    current_user: Annotated[User, Depends(get_current_active_user)],
    service: ItemService = Depends(get_item_service)
):
    set_cache_headers(response)
    items = service.get_all_items()
    return [
        ItemResponse(
            id=item.id,
            name=item.name,
            description=item.description,
            links=create_item_links(item.id, request)
        )
        for item in items
    ]


@router.get("/{item_id}", response_model=ItemResponse, dependencies=[Depends(validate_accept)])
def get_item(
    item_id: int,
    request: Request,
    response: Response,
    current_user: Annotated[User, Depends(get_current_active_user)],
    service: ItemService = Depends(get_item_service)
):
    set_cache_headers(response)
    item = service.get_item(item_id)
    return ItemResponse(
        id=item.id,
        name=item.name,
        description=item.description,
        links=create_item_links(item.id, request)
    )


@router.put("/{item_id}", response_model=ItemResponse, dependencies=[Depends(validate_content_type), Depends(validate_accept)])
def update_item(
    item_id: int,
    item: ItemUpdateRequest,
    request: Request,
    response: Response,
    current_user: Annotated[User, Depends(get_current_active_user)],
    service: ItemService = Depends(get_item_service)
):
    set_no_cache_headers(response)
    item_model = Item(name=item.name, description=item.description)
    updated_item = service.update_item(item_id, item_model)
    return ItemResponse(
        id=updated_item.id,
        name=updated_item.name,
        description=updated_item.description,
        links=create_item_links(updated_item.id, request)
    )


@router.delete("/{item_id}", response_model=ItemResponse, status_code=200, dependencies=[Depends(validate_accept)])
def delete_item(
    item_id: int,
    request: Request,
    response: Response,
    current_user: Annotated[User, Depends(get_current_active_user)],
    service: ItemService = Depends(get_item_service)
):
    set_no_cache_headers(response)
    item = service.get_item(item_id)
    service.delete_item(item_id)
    return ItemResponse(
        id=item.id,
        name=item.name,
        description=item.description,
        links=create_item_links(item.id, request)
    )
