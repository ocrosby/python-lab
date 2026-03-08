# infrastructure/security

Security services providing authentication, authorisation, and protection capabilities.
These are infrastructure concerns: they depend on third-party libraries (python-jose,
passlib, pyotp) and the persistence layer.

## Files

| File | Class | Description |
|---|---|---|
| `password_hasher.py` | `PasswordHasher` | bcrypt password hashing and verification |
| `jwt_handler.py` | `JWTHandler` | JWT access and refresh token creation/validation |
| `rate_limiter.py` | `RateLimiter` | In-memory per-IP request rate tracking |
| `account_lockout.py` | `AccountLockoutService` | Tracks and enforces account lockout |
| `mfa_service.py` | `MFAService` | TOTP secret generation and code verification |
| `audit_logger.py` | `AuditLogger` | Persists security events to the database |
| `token_blacklist.py` | `TokenBlacklistService` | Tracks revoked tokens after logout |

## PasswordHasher

Wraps `passlib[bcrypt]`. Use `hash(plain)` to create a hash and `verify(plain, hashed)`
to check credentials.

## JWTHandler

Issues short-lived access tokens and longer-lived refresh tokens using `python-jose`.
Validates tokens and extracts claims.

## RateLimiter

Counts requests per IP in a sliding window. Used by `RateLimitMiddleware` in
`infrastructure/logging/middleware.py`. Configured via `rate_limit_requests_per_minute`
in settings.

## AccountLockoutService

Increments and checks `failed_login_attempts` and `locked_until` on the `User` entity to
prevent brute-force attacks.

## MFAService

Generates TOTP secrets and QR code URIs for authenticator apps (Google Authenticator,
Authy, etc.). Verifies TOTP codes using `pyotp`.

## AuditLogger

Appends `AuditLogModel` records to the database for security-relevant events: login
attempts, password changes, MFA setup, and token revocation.

## TokenBlacklistService

After logout, tokens are stored in `TokenBlacklistModel` so they cannot be reused even
if they have not yet expired.

See `../README.md` for the full infrastructure layer overview.
