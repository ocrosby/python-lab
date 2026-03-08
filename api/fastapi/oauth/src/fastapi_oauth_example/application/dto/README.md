# application/dto

Data Transfer Objects (DTOs) define the shapes of data crossing the boundary between the
application core and adapters. They are Pydantic `BaseModel` subclasses, providing
automatic validation and JSON serialisation.

## Files

| File | Description |
|---|---|
| `user_dto.py` | All request and response DTOs for auth and user operations |

## DTOs

| Class | Direction | Used by |
|---|---|---|
| `UserRegistrationDTO` | Input | `POST /api/v1/auth/register` |
| `UserLoginDTO` | Input | `POST /api/v1/auth/login` |
| `TokenDTO` | Output | Login and token refresh responses |
| `RefreshTokenDTO` | Input | Token refresh endpoint |
| `UserResponseDTO` | Output | `GET /api/v1/auth/me` |
| `PasswordResetRequestDTO` | Input | Password reset request |
| `PasswordResetDTO` | Input | Password reset completion |
| `EmailVerificationDTO` | Input | Email verification |
| `MFASetupResponseDTO` | Output | MFA setup (QR code + secret) |
| `MFAVerifyDTO` | Input | MFA code verification |
| `SessionResponseDTO` | Output | Active session listing |

DTOs are **not** domain entities. They exist to decouple the wire format from internal
domain objects. If the API shape needs to change (e.g. rename a field, add versioning),
only the DTO and its mapping code change — the domain entity is unaffected.
