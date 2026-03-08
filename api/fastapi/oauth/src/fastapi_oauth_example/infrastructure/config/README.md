# infrastructure/config

Application configuration loaded from environment variables and `.env` files using
Pydantic `BaseSettings`.

## Files

| File | Description |
|---|---|
| `settings.py` | `Settings` class + module-level `settings` singleton |

## Settings

All configuration is centralised in a single `Settings` instance accessible as
`from fastapi_oauth_example.infrastructure.config.settings import settings`.

| Field | Default | Description |
|---|---|---|
| `database_url` | `postgresql+asyncpg://...` | SQLAlchemy async database URL |
| `secret_key` | — | JWT signing secret (must be set in production) |
| `algorithm` | `HS256` | JWT signing algorithm |
| `access_token_expire_minutes` | `30` | Access token lifetime |
| `refresh_token_expire_days` | `7` | Refresh token lifetime |
| `max_login_attempts` | `5` | Failed attempts before account lockout |
| `lockout_duration_minutes` | `15` | Duration of account lockout |
| `password_reset_token_expire_hours` | `1` | Password reset token lifetime |
| `email_verification_token_expire_hours` | `24` | Email verification token lifetime |
| `rate_limit_requests_per_minute` | `5` | Per-IP rate limit |
| `cors_origins` | `[...]` | Allowed CORS origins |
| `cors_allow_credentials` | `true` | CORS credentials flag |
| `cors_allow_methods` | `["*"]` | Allowed HTTP methods |
| `cors_allow_headers` | `["*"]` | Allowed request headers |
| `allowed_hosts` | `[...]` | `TrustedHostMiddleware` allowlist |
| `gzip_minimum_size` | `1000` | Minimum response size to compress (bytes) |
| `gzip_compression_level` | `5` | Gzip compression level (1–9) |

All fields can be overridden via environment variables (uppercased) or a `.env` file.
See `.env.example` at the project root for a complete example.

See `../README.md` for the full infrastructure layer overview.
