# Query Parameter Validations

[◀ Back: Request Body](../02-getting-started/request-body.md) | [Index](../../README.md) | [Next: Path Validations ▶](path-validations.md)

## Quick Summary

Add advanced validation constraints to query parameters using `Query()` from FastAPI.

## Key Concepts

- **String Validation**: Length, regex patterns
- **Numeric Validation**: Min, max, multiple of
- **Metadata**: Title, description for documentation
- **Aliases**: Alternative parameter names

## Basic Example

```python
from fastapi import FastAPI, Query

app = FastAPI()

@app.get("/items/")
async def read_items(
    q: str | None = Query(None, min_length=3, max_length=50)
):
    return {"q": q}
```

## String Validations

```python
@app.get("/items/")
async def read_items(
    # Length constraints
    q: str | None = Query(None, min_length=3, max_length=50),
    
    # Regex pattern
    name: str | None = Query(None, pattern="^[a-zA-Z]+$"),
    
    # Required with constraints
    email: str = Query(..., regex=r"^[\w\.-]+@[\w\.-]+\.\w+$")
):
    return {"q": q, "name": name, "email": email}
```

## Numeric Validations

```python
@app.get("/items/")
async def read_items(
    # Greater than / less than
    price: float | None = Query(None, gt=0, le=1000),
    
    # Greater/less than or equal
    quantity: int = Query(1, ge=1, le=100),
    
    # Multiple of
    batch_size: int | None = Query(None, multiple_of=10)
):
    return {"price": price, "quantity": quantity}
```

## Required vs Optional

```python
@app.get("/items/")
async def read_items(
    # Required (no default, using ...)
    q: str = Query(..., min_length=3),
    
    # Optional with None
    filter: str | None = Query(None),
    
    # Optional with default value
    skip: int = Query(0, ge=0),
    
    # Required with validation
    limit: int = Query(..., gt=0, le=100)
):
    return {"q": q, "filter": filter, "skip": skip, "limit": limit}
```

## List Query Parameters

```python
@app.get("/items/")
async def read_items(
    # Accept multiple values
    tags: list[str] = Query([]),
    
    # With validation
    ids: list[int] | None = Query(None, min_length=1, max_length=10)
):
    return {"tags": tags, "ids": ids}
```

**URL**: `/items/?tags=python&tags=fastapi&ids=1&ids=2&ids=3`

## Metadata for Documentation

```python
@app.get("/items/")
async def read_items(
    q: str | None = Query(
        None,
        title="Query string",
        description="Search query to filter items",
        min_length=3,
        max_length=50,
        example="fastapi"
    )
):
    return {"q": q}
```

## Aliases

```python
@app.get("/items/")
async def read_items(
    # item-query in URL, but q in code
    q: str | None = Query(None, alias="item-query")
):
    return {"q": q}
```

**URL**: `/items/?item-query=test`

## Deprecated Parameters

```python
@app.get("/items/")
async def read_items(
    q: str | None = Query(None),
    old_param: str | None = Query(None, deprecated=True)
):
    return {"q": q}
```

## Quick Reference

```python
from fastapi import FastAPI, Query

app = FastAPI()

@app.get("/items/")
async def read_items(
    # String validation
    q: str | None = Query(None, min_length=3, max_length=50),
    
    # Numeric validation
    price: float = Query(..., gt=0, le=1000),
    
    # Pattern matching
    code: str | None = Query(None, pattern="^[A-Z]{3}$"),
    
    # List of values
    tags: list[str] = Query([]),
    
    # With metadata
    name: str = Query(..., title="Item name", description="Name of the item")
):
    return {"q": q, "price": price, "code": code, "tags": tags, "name": name}
```

## Related Topics

- [Path Validations](path-validations.md) - Validate path parameters
- [Query Parameter Models](query-models.md) - Pydantic models for queries
- [Body Fields](body-fields.md) - Validate request body fields
