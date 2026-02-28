# Request Body

[◀ Back: Query Parameters](query-parameters.md) | [Index](../../README.md) | [Next: Validation ▶](../03-validation/query-validations.md)

## Quick Summary

Accept JSON request bodies using Pydantic models for automatic validation, parsing, and documentation.

## Key Concepts

- **Pydantic Models**: Define request body structure
- **Automatic Validation**: Type checking and constraints
- **Auto Documentation**: Request body schema in Swagger UI
- **POST/PUT/PATCH**: HTTP methods that typically use request bodies

## Basic Example

```python
from fastapi import FastAPI
from pydantic import BaseModel

class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None

app = FastAPI()

@app.post("/items/")
async def create_item(item: Item):
    return item
```

**Request**:
```json
{
  "name": "Foo",
  "price": 45.2,
  "tax": 3.5
}
```

**Response**:
```json
{
  "name": "Foo",
  "description": null,
  "price": 45.2,
  "tax": 3.5
}
```

## Pydantic Model

```python
from pydantic import BaseModel

class Item(BaseModel):
    name: str                          # Required
    description: str | None = None     # Optional
    price: float                       # Required
    tax: float | None = None           # Optional
```

### Features
- **Type Validation**: Ensures correct data types
- **Default Values**: Optional fields with defaults
- **Nested Models**: Complex data structures
- **Automatic Docs**: Schema appears in OpenAPI

## Using the Model

```python
@app.post("/items/")
async def create_item(item: Item):
    # Access attributes
    item_dict = item.model_dump()
    
    # Calculate with tax
    if item.tax:
        price_with_tax = item.price + item.tax
    else:
        price_with_tax = item.price
    
    return {"price_with_tax": price_with_tax}
```

## Request Body + Path Parameters

```python
@app.put("/items/{item_id}")
async def update_item(item_id: int, item: Item):
    return {"item_id": item_id, **item.model_dump()}
```

**URL**: `PUT /items/42`
**Body**:
```json
{
  "name": "Updated Item",
  "price": 100.0
}
```

## Request Body + Path + Query Parameters

```python
@app.put("/items/{item_id}")
async def update_item(
    item_id: int,              # Path parameter
    item: Item,                # Request body
    q: str | None = None       # Query parameter
):
    result = {"item_id": item_id, **item.model_dump()}
    if q:
        result.update({"q": q})
    return result
```

**FastAPI knows**:
- Path from URL structure: `item_id`
- Body from Pydantic model: `item`
- Query from other parameters: `q`

## Common Patterns

### Create Resource

```python
class User(BaseModel):
    username: str
    email: str
    full_name: str | None = None

@app.post("/users/")
async def create_user(user: User):
    return {"username": user.username, "email": user.email}
```

### Update Resource

```python
@app.put("/users/{user_id}")
async def update_user(user_id: int, user: User):
    return {"user_id": user_id, "user": user}
```

### Partial Update

```python
class UserUpdate(BaseModel):
    username: str | None = None
    email: str | None = None
    full_name: str | None = None

@app.patch("/users/{user_id}")
async def partial_update_user(user_id: int, user: UserUpdate):
    return {"user_id": user_id, "updated_fields": user.model_dump(exclude_unset=True)}
```

## Multiple Body Parameters

```python
from pydantic import BaseModel

class Item(BaseModel):
    name: str
    price: float

class User(BaseModel):
    username: str

@app.put("/items/{item_id}")
async def update_item(item_id: int, item: Item, user: User):
    return {"item_id": item_id, "item": item, "user": user}
```

**Request body**:
```json
{
  "item": {
    "name": "Foo",
    "price": 45.2
  },
  "user": {
    "username": "john"
  }
}
```

## Singular Values in Body

```python
from fastapi import Body

@app.put("/items/{item_id}")
async def update_item(
    item_id: int,
    item: Item,
    importance: int = Body()  # Singular value in body
):
    return {"item_id": item_id, "item": item, "importance": importance}
```

**Request body**:
```json
{
  "item": {
    "name": "Foo",
    "price": 45.2
  },
  "importance": 5
}
```

## Model Methods

```python
class Item(BaseModel):
    name: str
    price: float
    tax: float | None = None
    
    def calculate_total(self):
        return self.price + (self.tax or 0)

@app.post("/items/")
async def create_item(item: Item):
    total = item.calculate_total()
    return {"item": item, "total": total}
```

## Validation Example

```python
from pydantic import BaseModel, Field

class Item(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    price: float = Field(..., gt=0)
    tax: float | None = Field(None, ge=0)

@app.post("/items/")
async def create_item(item: Item):
    return item
```

## Error Response

**Invalid Request**:
```json
{
  "name": "",
  "price": -10
}
```

**Error Response**:
```json
{
  "detail": [
    {
      "type": "string_too_short",
      "loc": ["body", "name"],
      "msg": "String should have at least 1 character"
    },
    {
      "type": "greater_than",
      "loc": ["body", "price"],
      "msg": "Input should be greater than 0"
    }
  ]
}
```

## Quick Reference

```python
from fastapi import FastAPI
from pydantic import BaseModel

class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None

app = FastAPI()

# POST with body
@app.post("/items/")
async def create_item(item: Item):
    return item

# PUT with path + body
@app.put("/items/{item_id}")
async def update_item(item_id: int, item: Item):
    return {"item_id": item_id, **item.model_dump()}

# All three: path + query + body
@app.put("/items/{item_id}")
async def update_item_full(
    item_id: int,
    item: Item,
    q: str | None = None
):
    result = {"item_id": item_id, **item.model_dump()}
    if q:
        result["q"] = q
    return result
```

## Related Topics

- [Body Fields](../03-validation/body-fields.md) - Field-level validation
- [Nested Models](../03-validation/nested-models.md) - Complex structures
- [Multiple Parameters](../03-validation/body-multiple-params.md) - Multiple body params
- [Response Models](../05-responses/response-models.md) - Type-safe responses
