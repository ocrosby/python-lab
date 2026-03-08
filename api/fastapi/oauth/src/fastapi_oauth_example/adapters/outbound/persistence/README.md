# adapters/outbound/persistence

PostgreSQL persistence adapters. Implements storage-related ports using SQLAlchemy's
async ORM against a PostgreSQL database.

## Files

| File | Class(es) | Port implemented |
|---|---|---|
| `database.py` | `Database` | SQLAlchemy async engine + session factory |
| `models.py` | `UserModel`, `RefreshTokenModel`, `TokenBlacklistModel`, `AuditLogModel`, `SessionModel`, `PasswordResetTokenModel`, `EmailVerificationTokenModel` | ORM table definitions |
| `postgres_user_repository.py` | `PostgresUserRepository` | `UserRepository` |
| `token_repositories.py` | `RefreshTokenRepository`, `PasswordResetTokenRepository`, `EmailVerificationTokenRepository`, `SessionRepository` | Token/session storage |

## PostgresUserRepository

Implements the `UserRepository` port using SQLAlchemy async ORM. Each method receives an
`AsyncSession` injected by the DI container.

```python
repo = PostgresUserRepository(session)
user = await repo.get_by_email("user@example.com")
await repo.save(user)
```

## Replacing with a different database

1. Create `<db>_user_repository.py` in this directory implementing `UserRepository`.
2. In `infrastructure/di/dependencies.py`, update `get_user_repository()` to return the
   new class.

Because `get_user_repository()` is typed to return `UserRepository` (the abstract port),
no call sites outside `dependencies.py` need to change.

See `../../README.md` for the full adapters layer overview.
