# application

The **application** package orchestrates the domain. It sits between the domain (what the
business rules are) and the adapters (how the outside world interacts). It is the layer
that knows *what to do* but not *how* infrastructure works.

Dependencies allowed from this layer:
- `domain/` — entities, value objects
- `ports/` — abstract repository and service contracts
- `infrastructure/` — only cross-cutting concerns (DI annotations)

Dependencies **not** allowed:
- `adapters/` — no concrete HTTP, persistence, or messaging code
- FastAPI request/response types — DTOs are plain Pydantic models, not `Request`/`Response`

---

## Package layout

```
application/
├── dto/
│   └── user_dto.py                      # data transfer objects (Pydantic models)
├── services/
│   ├── health_service.py                # health / probe business logic
│   └── email_service.py                 # email sending abstraction
└── use_cases/
    ├── register_user_use_case.py
    ├── login_user_use_case.py
    ├── verify_token_use_case.py
    ├── refresh_token_use_case.py
    ├── password_reset_use_case.py
    └── email_verification_use_case.py
```

---

## dto/user_dto.py

Data Transfer Objects are the shapes of data crossing the boundary between the application
core and adapters. They are Pydantic `BaseModel` subclasses.

| DTO | Purpose |
|---|---|
| `UserRegistrationDTO` | Input for user registration |
| `UserLoginDTO` | Input for user login |
| `TokenDTO` | JWT access + refresh token response |
| `RefreshTokenDTO` | Input for token refresh |
| `UserResponseDTO` | User profile response |
| `PasswordResetRequestDTO` | Input for requesting a password reset |
| `PasswordResetDTO` | Input for completing a password reset |
| `EmailVerificationDTO` | Input for email verification |
| `MFASetupResponseDTO` | MFA setup response with QR code |
| `MFAVerifyDTO` | Input for MFA code verification |
| `SessionResponseDTO` | Active session information |

---

## services/

`HealthService` encapsulates liveness/readiness/startup probe logic.
`EmailService` is an abstract base for email delivery; `ConsoleEmailService` is the
development implementation that prints to stdout.

---

## use_cases/

Each use case is a single-responsibility class with an `execute()` method. Use cases
accept ports (from `ports/`) as constructor arguments — never concrete adapters.

| Use case | Responsibility |
|---|---|
| `RegisterUserUseCase` | Create and persist a new user account |
| `LoginUserUseCase` | Verify credentials and issue JWT tokens |
| `VerifyTokenUseCase` | Validate a JWT and return the authenticated user |
| `RefreshTokenUseCase` | Exchange a refresh token for a new access token |
| `RequestPasswordResetUseCase` | Generate and send a password reset token |
| `ResetPasswordUseCase` | Apply a new password using a reset token |
| `SendEmailVerificationUseCase` | Send an email verification link |
| `VerifyEmailUseCase` | Mark an email address as verified |

---

## Adding a new use case

1. Create `application/use_cases/<verb>_<noun>_use_case.py`.
2. Accept ports (from `ports/`) as constructor arguments — never concrete adapters.
3. Return a DTO from `application/dto/`.
4. Add a factory function in `infrastructure/di/dependencies.py`.
5. Inject via `Annotated[MyUseCase, Depends(get_my_use_case)]` in the router.
