# Query Parameters

[◀ Back: Path Parameters](path-parameters.md) | [Index](../../README.md) | [Next: Request Body ▶](request-body.md)

## Quick Summary

Handle URL query strings (`?key=value&key2=value2`) with automatic type conversion, defaults, and validation.

## Key Concepts

- **Query Parameters**: Key-value pairs after `?` in URL
- **Optional by Default**: Parameters with default values are optional
- **Type Conversion**: Automatic conversion based on type hints
- **Required Parameters**: Declare without default value

## Basic Example

```python
from fastapi import FastAPI

app = FastAPI()

fake_items_db = [
    {"item_name": "Foo"},
    {"item_name": "Bar"},
    {"item_name": "Baz"}
]

@app.get("/items/")
async def read_item(skip: int = 0, limit: int = 10):
    return fake_items_db[skip : skip + limit]
```

**URL**: `/items/?skip=0&limit=10`
- `skip`: defaults to `0`
- `limit`: defaults to `10`

## Default Values

```python
@app.get("/items/")
async def read_items(skip: int = 0, limit: int = 10):
    return {"skip": skip, "limit": limit}
```

**Examples**:
- `/items/` → `skip=0, limit=10` (uses defaults)
- `/items/?skip=20` → `skip=20, limit=10` (partial override)
- `/items/?skip=5&limit=20` → `skip=5, limit=20` (full override)

## Optional Parameters

```python
@app.get("/items/{item_id}")
async def read_item(item_id: str, q: str | None = None):
    if q:
        return {"item_id": item_id, "q": q}
    return {"item_id": item_id}
```

**Examples**:
- `/items/foo` → `{"item_id": "foo"}`
- `/items/foo?q=bar` → `{"item_id": "foo", "q": "bar"}`

### Python 3.8-3.9 Syntax

```python
from typing import Union

@app.get("/items/{item_id}")
async def read_item(item_id: str, q: Union[str, None] = None):
    if q:
        return {"item_id": item_id, "q": q}
    return {"item_id": item_id}
```

## Type Conversion

### Boolean Conversion

```python
@app.get("/items/{item_id}")
async def read_item(
    item_id: str,
    q: str | None = None,
    short: bool = False
):
    item = {"item_id": item_id}
    if q:
        item.update({"q": q})
    if not short:
        item.update({"description": "Long description here"})
    return item
```

**Boolean values** (`short` parameter):
- `1`, `True`, `true`, `on`, `yes` → `True`
- `0`, `False`, `false`, `off`, `no` → `False`

**Examples**:
- `/items/foo?short=1` → `short=True`
- `/items/foo?short=True` → `short=True`
- `/items/foo?short=yes` → `short=True`
- `/items/foo` → `short=False` (default)

## Multiple Parameters

```python
@app.get("/users/{user_id}/items/{item_id}")
async def read_user_item(
    user_id: int,
    item_id: str,
    q: str | None = None,
    short: bool = False
):
    item = {"item_id": item_id, "owner_id": user_id}
    if q:
        item.update({"q": q})
    if not short:
        item.update({"description": "Long description"})
    return item
```

**FastAPI automatically distinguishes**:
- Path parameters: `user_id`, `item_id`
- Query parameters: `q`, `short`

## Required Query Parameters

```python
@app.get("/items/{item_id}")
async def read_user_item(item_id: str, needy: str):
    return {"item_id": item_id, "needy": needy}
```

**No default value** = **Required parameter**

**Examples**:
- `/items/foo` → **422 Error** (missing `needy`)
- `/items/foo?needy=bar` → `{"item_id": "foo", "needy": "bar"}` ✅

## Mixed Required/Optional/Default

```python
@app.get("/items/{item_id}")
async def read_user_item(
    item_id: str,           # Path parameter (required)
    needy: str,             # Query parameter (required)
    skip: int = 0,          # Query parameter (optional with default)
    limit: int | None = None # Query parameter (optional, no default)
):
    item = {
        "item_id": item_id,
        "needy": needy,
        "skip": skip,
        "limit": limit
    }
    return item
```

**Parameter breakdown**:
- `item_id`: Path parameter (always required)
- `needy`: Required query parameter
- `skip`: Optional with default `0`
- `limit`: Optional, `None` if not provided

## Common Patterns

### Pagination

```python
@app.get("/items/")
async def list_items(page: int = 1, page_size: int = 50):
    start = (page - 1) * page_size
    end = start + page_size
    return {"items": items[start:end], "page": page, "page_size": page_size}
```

### Search with Filters

```python
@app.get("/products/")
async def search_products(
    q: str | None = None,
    category: str | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    in_stock: bool = True
):
    return {
        "query": q,
        "category": category,
        "price_range": (min_price, max_price),
        "in_stock": in_stock
    }
```

### Sort and Order

```python
@app.get("/items/")
async def list_items(
    sort_by: str = "created_at",
    order: str = "desc",
    limit: int = 100
):
    return {
        "sort_by": sort_by,
        "order": order,
        "limit": limit
    }
```

## Type Examples

```python
from datetime import date, datetime

@app.get("/search/")
async def search(
    q: str,                          # String
    limit: int = 10,                 # Integer
    offset: int = 0,                 # Integer
    price: float | None = None,      # Float
    tags: list[str] | None = None,   # List (see validation docs)
    available: bool = True,          # Boolean
    created_after: date | None = None # Date
):
    return {
        "q": q,
        "limit": limit,
        "offset": offset,
        "price": price,
        "available": available,
        "created_after": created_after
    }
```

## Error Responses

### Missing Required Parameter

```json
{
  "detail": [
    {
      "type": "missing",
      "loc": ["query", "needy"],
      "msg": "Field required",
      "input": null
    }
  ]
}
```

### Invalid Type

```json
{
  "detail": [
    {
      "type": "int_parsing",
      "loc": ["query", "limit"],
      "msg": "Input should be a valid integer",
      "input": "abc"
    }
  ]
}
```

## Quick Reference

```python
from fastapi import FastAPI

app = FastAPI()

# Optional with defaults
@app.get("/items/")
async def read_items(skip: int = 0, limit: int = 10):
    return {"skip": skip, "limit": limit}

# Required query parameter
@app.get("/search/")
async def search(q: str):
    return {"query": q}

# Mixed parameters
@app.get("/items/{item_id}")
async def read_item(
    item_id: int,              # Path (required)
    q: str | None = None,      # Query (optional)
    short: bool = False        # Query (optional with default)
):
    return {"item_id": item_id, "q": q, "short": short}
```

## Related Topics

- [Query Parameter Validations](../03-validation/query-validations.md) - Advanced validation (length, regex)
- [Query Parameter Models](../03-validation/query-models.md) - Pydantic models for queries
- [Path Parameters](path-parameters.md) - Dynamic URL segments
- [Request Body](request-body.md) - POST/PUT JSON data
