# Path Parameters

[◀ Back: First Steps](first-steps.md) | [Index](../../README.md) | [Next: Query Parameters ▶](query-parameters.md)

## Quick Summary

Capture dynamic values from URL paths with automatic type conversion and validation.

## Key Concepts

- **Path Parameters**: Variables in the URL path (e.g., `/items/{item_id}`)
- **Type Declaration**: Use Python type hints for automatic validation
- **Order Matters**: Declare specific paths before dynamic ones
- **Enums**: Restrict values to a predefined set

## Basic Example

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/items/{item_id}")
async def read_item(item_id: int):
    return {"item_id": item_id}
```

**URL**: `/items/5` → `{"item_id": 5}`

## Type Conversion & Validation

```python
@app.get("/items/{item_id}")
async def read_item(item_id: int):
    return {"item_id": item_id}
```

### Automatic Conversion
- URL: `/items/3` → `item_id = 3` (int)
- Returns: `{"item_id": 3}`

### Automatic Validation
- URL: `/items/foo` → **422 Error**
- Invalid type triggers validation error with clear message

## Supported Types

```python
# Integer
@app.get("/items/{item_id}")
async def get_int(item_id: int):
    return {"id": item_id}

# String
@app.get("/items/{item_id}")
async def get_str(item_id: str):
    return {"id": item_id}

# Float
@app.get("/items/{item_id}")
async def get_float(item_id: float):
    return {"id": item_id}

# UUID
from uuid import UUID

@app.get("/items/{item_id}")
async def get_uuid(item_id: UUID):
    return {"id": item_id}
```

## Path Order Matters

```python
# ✅ CORRECT: Specific path first
@app.get("/users/me")
async def read_user_me():
    return {"user_id": "the current user"}

@app.get("/users/{user_id}")
async def read_user(user_id: str):
    return {"user_id": user_id}

# ❌ WRONG: Dynamic path would catch /users/me
@app.get("/users/{user_id}")
async def read_user(user_id: str):
    return {"user_id": user_id}

@app.get("/users/me")  # This will never be reached!
async def read_user_me():
    return {"user_id": "the current user"}
```

## Predefined Values with Enums

```python
from enum import Enum
from fastapi import FastAPI

class ModelName(str, Enum):
    alexnet = "alexnet"
    resnet = "resnet"
    lenet = "lenet"

app = FastAPI()

@app.get("/models/{model_name}")
async def get_model(model_name: ModelName):
    if model_name is ModelName.alexnet:
        return {"model_name": model_name, "message": "Deep Learning FTW!"}
    
    if model_name.value == "lenet":
        return {"model_name": model_name, "message": "LeCNN all the images"}
    
    return {"model_name": model_name, "message": "Have some residuals"}
```

### Enum Features
- **Type Safety**: Only accepts defined values
- **Auto Documentation**: Shows dropdown in Swagger UI
- **Member Comparison**: `model_name is ModelName.alexnet`
- **Value Access**: `model_name.value`
- **Auto Conversion**: Returns as string in JSON

## Path Parameters Containing Paths

```python
@app.get("/files/{file_path:path}")
async def read_file(file_path: str):
    return {"file_path": file_path}
```

**Examples**:
- `/files/home/user/doc.txt` → `file_path = "home/user/doc.txt"`
- `/files//home/user/doc.txt` → `file_path = "/home/user/doc.txt"` (note double `/`)

## Multiple Path Parameters

```python
@app.get("/users/{user_id}/items/{item_id}")
async def read_user_item(user_id: int, item_id: str):
    return {"user_id": user_id, "item_id": item_id}
```

**URL**: `/users/42/items/foo` → `{"user_id": 42, "item_id": "foo"}`

## Common Patterns

### Resource by ID

```python
@app.get("/users/{user_id}")
async def get_user(user_id: int):
    return {"user_id": user_id}

@app.get("/posts/{post_id}")
async def get_post(post_id: int):
    return {"post_id": post_id}
```

### Nested Resources

```python
@app.get("/users/{user_id}/posts/{post_id}")
async def get_user_post(user_id: int, post_id: int):
    return {"user_id": user_id, "post_id": post_id}
```

### Date Parameters

```python
from datetime import date

@app.get("/events/{event_date}")
async def get_events(event_date: date):
    return {"date": event_date}
```

**URL**: `/events/2024-01-15` → Automatically parsed to `date` object

## Error Responses

### Invalid Type
```json
{
  "detail": [
    {
      "type": "int_parsing",
      "loc": ["path", "item_id"],
      "msg": "Input should be a valid integer",
      "input": "foo"
    }
  ]
}
```

### Invalid Enum Value
```json
{
  "detail": [
    {
      "type": "enum",
      "loc": ["path", "model_name"],
      "msg": "Input should be 'alexnet', 'resnet' or 'lenet'",
      "input": "unknown"
    }
  ]
}
```

## Quick Reference

```python
from enum import Enum
from fastapi import FastAPI

app = FastAPI()

# Basic path parameter
@app.get("/items/{item_id}")
async def read_item(item_id: int):
    return {"item_id": item_id}

# Enum for predefined values
class Status(str, Enum):
    active = "active"
    inactive = "inactive"

@app.get("/status/{status}")
async def get_status(status: Status):
    return {"status": status}

# Path containing paths
@app.get("/files/{file_path:path}")
async def read_file(file_path: str):
    return {"file_path": file_path}
```

## Related Topics

- [Query Parameters](query-parameters.md) - URL query strings
- [Path Parameter Validations](../03-validation/path-validations.md) - Advanced validation
- [Request Body](request-body.md) - POST/PUT data
