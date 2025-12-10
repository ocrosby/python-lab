from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr


class Item(BaseModel):
    name: str
    description: str


class Link(BaseModel):
    href: str
    rel: str
    method: str = "GET"


class ItemInDB(BaseModel):
    id: int
    name: str
    description: str
    links: Optional[list[Link]] = None


class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str


class User(BaseModel):
    id: int
    email: str
    username: str
    is_active: bool = True


class UserInDB(User):
    hashed_password: str


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenData(BaseModel):
    username: Optional[str] = None


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class RefreshTokenInDB(BaseModel):
    id: int
    user_id: int
    token: str
    token_family: str
    expires_at: datetime
    created_at: datetime
    revoked: bool = False
