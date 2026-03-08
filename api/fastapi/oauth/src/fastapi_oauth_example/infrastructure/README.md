# infrastructure

The **infrastructure** package provides cross-cutting technical concerns that support the
whole application without belonging to any single layer. It does not contain business logic.
Code here can be used by any other package — domain, application, ports, or adapters — but
this package itself depends only on third-party libraries and the Python standard library.

---

## Package layout

```
infrastructure/
├── config/
│   └── settings.py          # application settings (Pydantic BaseSettings)
├── di/
│   └── dependencies.py      # FastAPI dependency factory functions
├── logging/
│   └── middleware.py        # ASGI middleware (request ID, logging, timing, security)
└── security/
    ├── account_lockout.py   # account lockout logic
    ├── audit_logger.py      # security event audit logging
    ├── jwt_handler.py       # JWT token creation and validation
    ├── mfa_service.py       # TOTP multi-factor authentication
    ├── password_hasher.py   # bcrypt password hashing
    ├── rate_limiter.py      # per-IP rate limiting
    └── token_blacklist.py   # revoked token tracking
```

---

## config/settings.py

Application settings loaded from environment variables using Pydantic `BaseSettings`.
Covers database connection, JWT configuration, security policy, rate limiting, CORS,
and compression settings.

---

## di/dependencies.py

FastAPI dependency factory functions. This is the **only** place where abstract ports
are bound to concrete adapter implementations. All factory functions return abstract
types (`UserRepository`, etc.), never concrete classes.

---

## logging/middleware.py

ASGI middlewares that run for every request:

| Middleware | Responsibility |
|---|---|
| `RequestIDMiddleware` | Generates or propagates `X-Request-ID` |
| `LoggingMiddleware` | Logs method, path, status code, and duration |
| `TimingMiddleware` | Adds `X-Process-Time` response header |
| `SecurityHeadersMiddleware` | Sets `CSP`, `HSTS`, `X-Frame-Options`, and other security headers |
| `RateLimitMiddleware` | Enforces per-IP request rate limits |

---

## security/

| File | Description |
|---|---|
| `password_hasher.py` | bcrypt password hashing and verification |
| `jwt_handler.py` | JWT access and refresh token creation/validation |
| `rate_limiter.py` | In-memory per-IP request rate tracking |
| `account_lockout.py` | Tracks and enforces account lockout after failed logins |
| `mfa_service.py` | TOTP code generation and verification (pyotp) |
| `audit_logger.py` | Persists security events (login, logout, failed attempts) to the database |
| `token_blacklist.py` | Tracks revoked tokens to prevent reuse after logout |
