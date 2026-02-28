# Dependencies Basics

[◀ Back to Index](../../README.md) | [Next: Classes as Dependencies ▶](classes.md)

## Quick Summary

Dependency Injection system for code reuse, shared logic, database connections, security, and more.

## Key Concepts

- **Dependency Injection**: Declare what your code needs
- **`Depends()`**: Mark a parameter as a dependency
- **Code Reuse**: Share logic across endpoints
- **Type Safety**: Full editor support and validation

## Basic Example

```python
from fastapi import Depends, FastAPI

app = FastAPI()

async def common_parameters(q: str | None = None, skip: int = 0, limit: int = 100):
    return {"q": q, "skip": skip, "limit": limit}

@app.get("/items/")
async def read_items(commons: dict = Depends(common_parameters)):
    return commons

@app.get("/users/")
async def read_users(commons: dict = Depends(common_parameters)):
    return commons
```

**Benefits**:
- Reusable logic
- Declared once, used everywhere
- Automatic parameter handling

## Dependency Function

```python
async def common_parameters(
    q: str | None = None,
    skip: int = 0,
    limit: int = 100
):
    return {"q": q, "skip": skip, "limit": limit}
```

**Features**:
- Can be `async` or `def`
- Can have parameters (query, path, body, etc.)
- Returns any value
- Can raise exceptions

## Using Dependencies

```python
@app.get("/items/")
async def read_items(commons: dict = Depends(common_parameters)):
    # commons contains the return value from common_parameters
    return {"query": commons["q"], "skip": commons["skip"]}
```

**FastAPI will**:
1. Call `common_parameters` with correct arguments
2. Get the result
3. Assign it to `commons`

## Common Patterns

### Database Session

```python
from sqlalchemy.orm import Session

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/users/")
async def read_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return users
```

### Current User

```python
async def get_current_user(token: str = Depends(oauth2_scheme)):
    user = decode_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    return user

@app.get("/users/me")
async def read_user_me(current_user: User = Depends(get_current_user)):
    return current_user
```

### Query Parameters Object

```python
from pydantic import BaseModel

class Pagination(BaseModel):
    skip: int = 0
    limit: int = 100

def get_pagination(skip: int = 0, limit: int = 100) -> Pagination:
    return Pagination(skip=skip, limit=limit)

@app.get("/items/")
async def read_items(pagination: Pagination = Depends(get_pagination)):
    return {"skip": pagination.skip, "limit": pagination.limit}
```

### Settings/Configuration

```python
from functools import lru_cache
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "My API"
    admin_email: str

@lru_cache()
def get_settings():
    return Settings()

@app.get("/info")
async def info(settings: Settings = Depends(get_settings)):
    return {"app_name": settings.app_name}
```

## Dependencies with Parameters

```python
def pagination(skip: int = 0, limit: int = 100):
    return {"skip": skip, "limit": limit}

@app.get("/items/")
async def read_items(
    commons: dict = Depends(pagination)
):
    return commons
```

**URL**: `/items/?skip=10&limit=20`
**Result**: `{"skip": 10, "limit": 20}`

## Multiple Dependencies

```python
async def verify_token(x_token: str = Header()):
    if x_token != "secret-token":
        raise HTTPException(status_code=400, detail="Invalid token")

async def verify_key(x_key: str = Header()):
    if x_key != "secret-key":
        raise HTTPException(status_code=400, detail="Invalid key")

@app.get("/items/")
async def read_items(
    token: None = Depends(verify_token),
    key: None = Depends(verify_key)
):
    return {"message": "Valid credentials"}
```

## Return Types

```python
# Return dict
def get_settings() -> dict:
    return {"debug": True}

# Return Pydantic model
def get_user() -> User:
    return User(username="john")

# Return None (for validation only)
def verify_token(token: str) -> None:
    if not is_valid(token):
        raise HTTPException(status_code=401)
```

## Dependency Execution

```python
async def dependency_a():
    print("dependency_a called")
    return "A"

async def dependency_b():
    print("dependency_b called")
    return "B"

@app.get("/")
async def read_root(
    a: str = Depends(dependency_a),
    b: str = Depends(dependency_b)
):
    return {"a": a, "b": b}
```

**Execution order**:
1. `dependency_a()` called → prints "dependency_a called"
2. `dependency_b()` called → prints "dependency_b called"
3. Path operation function called

## Error Handling in Dependencies

```python
async def get_user(user_id: int):
    user = await fetch_user(user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    return user

@app.get("/users/{user_id}")
async def read_user(user: User = Depends(get_user)):
    return user
```

**Benefits**:
- Error handling in one place
- Automatic HTTP exception conversion
- Clean endpoint code

## Quick Reference

```python
from fastapi import Depends, FastAPI, Header, HTTPException

app = FastAPI()

# Simple dependency
async def common_params(q: str | None = None, skip: int = 0):
    return {"q": q, "skip": skip}

# Database dependency
def get_db():
    db = Database()
    try:
        yield db
    finally:
        db.close()

# Authentication dependency
async def get_current_user(token: str = Header()):
    user = verify_token(token)
    if not user:
        raise HTTPException(status_code=401)
    return user

# Using dependencies
@app.get("/items/")
async def read_items(
    commons: dict = Depends(common_params),
    db: Database = Depends(get_db),
    user: User = Depends(get_current_user)
):
    return {"user": user, "params": commons}
```

## Related Topics

- [Classes as Dependencies](classes.md) - Use classes for dependencies
- [Sub-dependencies](sub-dependencies.md) - Dependencies with dependencies
- [Path Operation Dependencies](path-operation.md) - Dependencies in decorators
- [Global Dependencies](global.md) - App-wide dependencies
- [Dependencies with Yield](yield.md) - Setup and teardown
