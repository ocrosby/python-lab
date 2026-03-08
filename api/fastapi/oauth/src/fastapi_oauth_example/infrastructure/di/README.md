# infrastructure/di

Dependency injection wiring. This is the **only** place in the codebase where abstract
ports are bound to concrete adapter implementations.

## Files

| File | Description |
|---|---|
| `dependencies.py` | FastAPI `Depends()`-compatible factory functions |

## Factory functions

| Function | Return type | Concrete class created |
|---|---|---|
| `get_db_session()` | `AsyncSession` | SQLAlchemy async session |
| `get_password_hasher()` | `PasswordHasher` | `PasswordHasher` |
| `get_jwt_handler()` | `JWTHandler` | `JWTHandler` |
| `get_user_repository(session)` | `UserRepository` | `PostgresUserRepository` |
| `get_register_user_use_case(...)` | `RegisterUserUseCase` | `RegisterUserUseCase` |
| `get_login_user_use_case(...)` | `LoginUserUseCase` | `LoginUserUseCase` |
| `get_verify_token_use_case(...)` | `VerifyTokenUseCase` | `VerifyTokenUseCase` |
| `get_current_user(token, ...)` | authenticated user | result of `VerifyTokenUseCase.execute()` |

All functions that return ports return the **abstract** type, never the concrete
implementation. This allows tests to override a single factory via
`app.dependency_overrides` without touching any call site.

## Dependency graph

```
get_current_user
└── get_verify_token_use_case
    ├── get_user_repository → PostgresUserRepository (satisfies UserRepository)
    │   └── get_db_session
    └── get_jwt_handler

get_login_user_use_case
├── get_user_repository
├── get_password_hasher
└── get_jwt_handler

get_register_user_use_case
├── get_user_repository
└── get_password_hasher
```

## Swapping an adapter

1. Create the new adapter in `adapters/outbound/persistence/`.
2. Update the relevant factory function here to return the new concrete class.
3. No other files change.

See `../README.md` for the full infrastructure layer overview.
