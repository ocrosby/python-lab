# Security - First Steps

[◀ Back to Index](../../README.md) | [Next: Get Current User ▶](current-user.md)

## Quick Summary

Implement basic security with OAuth2 password flow using FastAPI's security utilities.

## Key Concepts

- **OAuth2PasswordBearer**: Token-based authentication
- **Security Schemes**: OpenAPI security definitions
- **Token Authentication**: Bearer tokens in headers
- **Automatic Docs**: Lock icon in Swagger UI

## Basic Example

```python
from fastapi import Depends, FastAPI
from fastapi.security import OAuth2PasswordBearer

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@app.get("/items/")
async def read_items(token: str = Depends(oauth2_scheme)):
    return {"token": token}
```

**Features**:
- Extracts token from `Authorization: Bearer <token>` header
- Shows lock icon in docs
- Returns 401 if missing

## OAuth2PasswordBearer

```python
from fastapi.security import OAuth2PasswordBearer

# tokenUrl is the endpoint where users get tokens
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
```

**What it does**:
- Looks for `Authorization` header
- Expects value: `Bearer <token>`
- Returns the token string
- Raises 401 if not found

## Using in Endpoints

```python
@app.get("/users/me")
async def read_users_me(token: str = Depends(oauth2_scheme)):
    # token contains the actual token string
    return {"token": token}
```

**Request**:
```
GET /users/me
Authorization: Bearer my-secret-token
```

**Response**:
```json
{
  "token": "my-secret-token"
}
```

## Token Endpoint

```python
from fastapi.security import OAuth2PasswordRequestForm

@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    # form_data.username
    # form_data.password
    
    # Verify credentials (simplified)
    if form_data.username != "user" or form_data.password != "pass":
        raise HTTPException(status_code=400, detail="Incorrect credentials")
    
    # Return token
    return {"access_token": "fake-token", "token_type": "bearer"}
```

**Request** (form data):
```
POST /token
Content-Type: application/x-www-form-urlencoded

username=user&password=pass
```

**Response**:
```json
{
  "access_token": "fake-token",
  "token_type": "bearer"
}
```

## Common Patterns

### Protect Specific Routes

```python
# Public route
@app.get("/")
async def public_route():
    return {"message": "Public"}

# Protected route
@app.get("/protected")
async def protected_route(token: str = Depends(oauth2_scheme)):
    return {"message": "Protected", "token": token}
```

### Extract User from Token

```python
async def get_current_user(token: str = Depends(oauth2_scheme)):
    # Decode token (simplified)
    user = decode_token(token)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

@app.get("/users/me")
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user
```

### Fake Token Verification

```python
fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
    }
}

def fake_decode_token(token: str):
    # This is fake - use real JWT decoding in production
    return fake_users_db.get(token)

async def get_current_user(token: str = Depends(oauth2_scheme)):
    user = fake_decode_token(token)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user
```

## Security Models

```python
from pydantic import BaseModel

class Token(BaseModel):
    access_token: str
    token_type: str

class User(BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = None

class UserInDB(User):
    hashed_password: str
```

## HTTP Exceptions for Auth

```python
from fastapi import HTTPException, status

# 401 Unauthorized
raise HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)

# 403 Forbidden
raise HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="Not enough permissions"
)
```

## Complete Example

```python
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class User(BaseModel):
    username: str
    email: str | None = None

fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "email": "johndoe@example.com",
        "hashed_password": "fakehashedsecret"
    }
}

def fake_hash_password(password: str):
    return "fakehashed" + password

def fake_decode_token(token: str):
    return User(
        username=token + "fakedecoded",
        email="john@example.com"
    )

async def get_current_user(token: str = Depends(oauth2_scheme)):
    user = fake_decode_token(token)
    return user

@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user_dict = fake_users_db.get(form_data.username)
    if not user_dict:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    
    hashed_password = fake_hash_password(form_data.password)
    if not hashed_password == user_dict["hashed_password"]:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    
    return {"access_token": form_data.username, "token_type": "bearer"}

@app.get("/users/me")
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user
```

## Testing in Swagger UI

1. Click lock icon 🔒
2. Enter username and password
3. Click "Authorize"
4. Token is automatically added to requests

## Quick Reference

```python
from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

app = FastAPI()

# Setup OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Token endpoint
@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    # Verify credentials
    if form_data.username == "user" and form_data.password == "pass":
        return {"access_token": form_data.username, "token_type": "bearer"}
    raise HTTPException(status_code=400, detail="Invalid credentials")

# Get current user
async def get_current_user(token: str = Depends(oauth2_scheme)):
    # Decode and verify token
    user = verify_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    return user

# Protected endpoint
@app.get("/users/me")
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user
```

## Related Topics

- [Get Current User](current-user.md) - Full user extraction
- [OAuth2 with Password](oauth2-password.md) - Complete password flow
- [OAuth2 with JWT](oauth2-jwt.md) - JWT tokens and hashing
- [OAuth2 Scopes](oauth2-scopes.md) - Permissions system
- [HTTP Basic Auth](http-basic-auth.md) - Alternative auth method
