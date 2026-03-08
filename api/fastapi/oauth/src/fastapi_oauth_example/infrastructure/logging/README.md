# infrastructure/logging

ASGI middleware and request lifecycle cross-cutting concerns.

## Files

| File | Description |
|---|---|
| `middleware.py` | All ASGI middlewares registered in `main.py` |

## Middlewares

| Class | Responsibility |
|---|---|
| `RequestIDMiddleware` | Generates or propagates `X-Request-ID` on every request |
| `LoggingMiddleware` | Logs method, path, status code, and duration at request end |
| `TimingMiddleware` | Adds `X-Process-Time` response header |
| `SecurityHeadersMiddleware` | Sets `Content-Security-Policy`, `Strict-Transport-Security`, `X-Frame-Options`, `X-Content-Type-Options`, and `Referrer-Policy` headers |
| `RateLimitMiddleware` | Enforces per-IP rate limits using the `RateLimiter` service |

## Registration order

Middleware is registered in `main.py` outermost-first (last registered = outermost wrapper):

```
TrustedHostMiddleware   (outermost)
CORSMiddleware
GZipMiddleware
RateLimitMiddleware
SecurityHeadersMiddleware
TimingMiddleware
LoggingMiddleware
RequestIDMiddleware     (innermost)
```

Request flow is outermost → innermost; response flow is innermost → outermost.

See `../README.md` for the full infrastructure layer overview.
