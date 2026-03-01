from dataclasses import dataclass
from datetime import datetime

from fastapi_oauth_example.domain.value_objects.email import Email
from fastapi_oauth_example.domain.value_objects.user_id import UserId


@dataclass
class User:
    id: UserId
    email: Email
    username: str
    hashed_password: str
    is_active: bool = True
    is_verified: bool = False
    email_verified_at: datetime | None = None
    failed_login_attempts: int = 0
    locked_until: datetime | None = None
    mfa_enabled: bool = False
    mfa_secret: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
