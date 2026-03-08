# domain/entities

Domain entities are the core business objects identified by a unique ID. They encapsulate
state and enforce invariants. Entities are plain Python dataclasses — no Pydantic, no ORM.

## Files

| File | Class | Description |
|---|---|---|
| `user.py` | `User` | Authenticated user with credentials, MFA, and lockout state |

## User

The central domain entity representing a registered user.

Key fields:
- `id: UUID` — unique identifier
- `email: str` — verified email address
- `hashed_password: str` — bcrypt-hashed password
- `is_active: bool` — whether the account is active
- `is_verified: bool` — whether the email has been verified
- `mfa_enabled: bool` — whether TOTP MFA is enabled
- `mfa_secret: str | None` — TOTP secret for MFA
- `failed_login_attempts: int` — consecutive failed logins (for lockout)
- `locked_until: datetime | None` — account lock expiry

Entities are created in use cases and persisted via the `UserRepository` port. They are
never created directly in route handlers or persistence code.
