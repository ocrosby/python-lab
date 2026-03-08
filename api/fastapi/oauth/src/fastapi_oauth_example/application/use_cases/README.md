# application/use_cases

Each use case is a single-responsibility class that orchestrates domain objects and ports
to fulfil one user-facing action. Use cases contain business logic; they are unaware of
HTTP, databases, or any infrastructure concern.

## Pattern

```python
class SomeUseCase:
    def __init__(self, user_repository: UserRepository, ...):
        ...  # accept ports, never concrete adapters

    async def execute(self, dto: SomeInputDTO) -> SomeOutputDTO:
        ...  # business logic
```

## Files

| File | Class(es) | Responsibility |
|---|---|---|
| `register_user_use_case.py` | `RegisterUserUseCase` | Create and persist a new user account |
| `login_user_use_case.py` | `LoginUserUseCase` | Verify credentials and issue JWT tokens |
| `verify_token_use_case.py` | `VerifyTokenUseCase` | Validate a JWT and return the user |
| `refresh_token_use_case.py` | `RefreshTokenUseCase` | Exchange refresh token for new access token |
| `password_reset_use_case.py` | `RequestPasswordResetUseCase`, `ResetPasswordUseCase` | Password reset flow |
| `email_verification_use_case.py` | `SendEmailVerificationUseCase`, `VerifyEmailUseCase` | Email verification flow |

## Adding a new use case

1. Create `<verb>_<noun>_use_case.py` in this directory.
2. Accept `UserRepository` and other ports from `ports/outbound/` as constructor args.
3. Return a DTO from `application/dto/`.
4. Add a factory function in `infrastructure/di/dependencies.py`.
5. Inject via `Annotated[MyUseCase, Depends(get_my_use_case)]` in the router.
