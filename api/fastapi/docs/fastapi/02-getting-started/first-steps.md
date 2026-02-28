# First Steps

[◀ Back to Index](../../README.md) | [Next: Path Parameters ▶](path-parameters.md)

## Quick Summary

Create your first FastAPI application with automatic interactive documentation.

## Key Concepts

- **FastAPI Instance**: Main application object
- **Path Operations**: Routes that handle HTTP requests
- **Decorators**: `@app.get()`, `@app.post()`, etc.
- **Automatic Docs**: Swagger UI at `/docs`, ReDoc at `/redoc`

## Basic Example

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}
```

## Running the App

```bash
# Development mode (with auto-reload)
fastapi dev main.py

# Production mode
fastapi run main.py
```

## Step-by-Step Breakdown

### 1. Import FastAPI

```python
from fastapi import FastAPI
```

### 2. Create App Instance

```python
app = FastAPI()
```

### 3. Define Path Operation

```python
@app.get("/")
async def root():
    return {"message": "Hello World"}
```

- **Path**: `/` (root path)
- **Operation**: `GET` HTTP method
- **Function**: `root()` handles the request

### 4. Return Content

```python
return {"message": "Hello World"}
```

Can return:
- `dict`, `list`
- Primitive values: `str`, `int`, `float`, `bool`
- Pydantic models
- Many other types (automatically converted to JSON)

## HTTP Methods/Operations

| Method | Purpose | Decorator |
|--------|---------|-----------|
| `GET` | Read data | `@app.get()` |
| `POST` | Create data | `@app.post()` |
| `PUT` | Update data | `@app.put()` |
| `DELETE` | Delete data | `@app.delete()` |
| `PATCH` | Partial update | `@app.patch()` |
| `OPTIONS` | Describe options | `@app.options()` |
| `HEAD` | Headers only | `@app.head()` |

## Interactive Documentation

After starting your app, visit:

- **Swagger UI**: `http://127.0.0.1:8000/docs`
- **ReDoc**: `http://127.0.0.1:8000/redoc`
- **OpenAPI JSON**: `http://127.0.0.1:8000/openapi.json`

## Async vs Sync

```python
# Async function (recommended for I/O operations)
@app.get("/async")
async def async_endpoint():
    return {"type": "async"}

# Sync function (for CPU-bound operations)
@app.get("/sync")
def sync_endpoint():
    return {"type": "sync"}
```

## Common Patterns

### Multiple Endpoints

```python
@app.get("/")
async def root():
    return {"message": "Root"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.get("/items")
async def list_items():
    return {"items": []}
```

### Different HTTP Methods

```python
@app.get("/items")
async def read_items():
    return {"method": "GET"}

@app.post("/items")
async def create_item():
    return {"method": "POST"}
```

## Related Topics

- [Path Parameters](path-parameters.md) - Dynamic URL segments
- [Query Parameters](query-parameters.md) - URL query strings
- [Request Body](request-body.md) - Accepting JSON data
- [Response Models](../05-responses/response-models.md) - Type-safe responses

## Quick Reference

```python
from fastapi import FastAPI

app = FastAPI()

# Basic endpoint
@app.get("/")
async def root():
    return {"message": "Hello"}

# Run with: fastapi dev main.py
# Docs at: http://127.0.0.1:8000/docs
```
