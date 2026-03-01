from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr


class UserRegistrationDTO(BaseModel):
    email: EmailStr
    username: str
    password: str


class UserLoginDTO(BaseModel):
    username: str
    password: str
    mfa_code: str | None = None


class TokenDTO(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenDTO(BaseModel):
    refresh_token: str


class UserResponseDTO(BaseModel):
    id: UUID
    email: str
    username: str
    is_active: bool
    is_verified: bool
    mfa_enabled: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PasswordResetRequestDTO(BaseModel):
    email: EmailStr


class PasswordResetDTO(BaseModel):
    token: str
    new_password: str


class EmailVerificationDTO(BaseModel):
    token: str


class MFASetupResponseDTO(BaseModel):
    secret: str
    qr_code_url: str


class MFAVerifyDTO(BaseModel):
    code: str


class SessionResponseDTO(BaseModel):
    id: UUID
    ip_address: str | None
    user_agent: str | None
    last_accessed_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True
