# FastAPI Quick Start Guide

This is a quick reference documentation for FastAPI. Each page is designed for minimal scrolling and quick lookup.

## Getting Started (5 minutes)

1. **[First Steps](fastapi/02-getting-started/first-steps.md)** - Your first FastAPI app
2. **[Path Parameters](fastapi/02-getting-started/path-parameters.md)** - Dynamic URL segments
3. **[Query Parameters](fastapi/02-getting-started/query-parameters.md)** - URL query strings
4. **[Request Body](fastapi/02-getting-started/request-body.md)** - Accepting JSON data

## Essential Concepts

### Request Handling
- **Path Parameters**: `/items/{item_id}` - Capture URL segments
- **Query Parameters**: `/items?skip=0&limit=10` - URL query strings
- **Request Body**: JSON payload with Pydantic models
- **Headers & Cookies**: Extract from HTTP headers

### Validation
- Automatic type conversion and validation
- Pydantic models for complex data
- Field-level constraints (min, max, regex)
- Clear error messages

### Dependencies
- **[Dependency Injection](fastapi/06-dependencies/basics.md)** - Code reuse and modularity
- Database sessions, authentication, configuration
- Sub-dependencies and dependency chains

### Security
- **[Security Basics](fastapi/07-security/first-steps.md)** - OAuth2 and authentication
- JWT tokens, password hashing
- Protected routes and permissions

## Document Structure

Each document follows this pattern:

```
# Topic Title

[Navigation Links]

## Quick Summary
Brief 1-line description

## Key Concepts
3-5 main ideas in bullet points

## Basic Example
Simple, copy-paste ready code

## Common Patterns
Real-world use cases

## Quick Reference
Cheat sheet at the end

## Related Topics
Links to related docs
```

## File Organization

```
docs/
├── README.md                     # Main index with all links
├── QUICKSTART.md                 # This file
└── fastapi/
    ├── 01-foundation/           # Python types, async, env vars
    ├── 02-getting-started/      # First steps, basics
    ├── 03-validation/           # Query/path/body validation
    ├── 04-input/               # Headers, cookies, forms, files
    ├── 05-responses/           # Response models, status codes
    ├── 06-dependencies/        # Dependency injection
    ├── 07-security/            # Authentication & authorization
    ├── 08-structure/           # App structure, middleware, testing
    ├── 09-advanced/            # Advanced features
    ├── 10-deployment/          # Docker, cloud, production
    └── 11-recipes/             # How-to guides
```

## Quick Examples

### Hello World
```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}
```

### Path & Query Parameters
```python
@app.get("/items/{item_id}")
async def read_item(item_id: int, q: str | None = None):
    return {"item_id": item_id, "q": q}
```

### Request Body
```python
from pydantic import BaseModel

class Item(BaseModel):
    name: str
    price: float

@app.post("/items/")
async def create_item(item: Item):
    return item
```

### Dependencies
```python
from fastapi import Depends

async def common_params(q: str | None = None, skip: int = 0):
    return {"q": q, "skip": skip}

@app.get("/items/")
async def read_items(commons: dict = Depends(common_params)):
    return commons
```

### Security
```python
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@app.get("/users/me")
async def read_users_me(token: str = Depends(oauth2_scheme)):
    return {"token": token}
```

## Learning Path

### Beginner (Day 1)
1. [First Steps](fastapi/02-getting-started/first-steps.md)
2. [Path Parameters](fastapi/02-getting-started/path-parameters.md)
3. [Query Parameters](fastapi/02-getting-started/query-parameters.md)
4. [Request Body](fastapi/02-getting-started/request-body.md)

### Intermediate (Day 2-3)
1. [Dependencies](fastapi/06-dependencies/basics.md)
2. [Security First Steps](fastapi/07-security/first-steps.md)
3. Error Handling
4. Response Models

### Advanced (Day 4-5)
1. Advanced Dependencies
2. OAuth2 with JWT
3. Background Tasks
4. WebSockets

### Production (Day 6-7)
1. Testing
2. Docker Deployment
3. Database Integration
4. Middleware

## Tips for Using These Docs

1. **Scan the Quick Summary** - Know what the page covers
2. **Copy the Basic Example** - Get started immediately
3. **Check Common Patterns** - See real-world usage
4. **Use Quick Reference** - Cheat sheet for fast lookup
5. **Follow Related Topics** - Deep dive when needed

## Next Steps

Start with the **[Full Index](README.md)** to see all available documentation, or jump right into **[First Steps](fastapi/02-getting-started/first-steps.md)** to build your first API.

## Official Resources

- [FastAPI Official Docs](https://fastapi.tiangolo.com/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Starlette Documentation](https://www.starlette.io/)
