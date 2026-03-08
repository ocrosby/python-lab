# infrastructure/logging

Structured logging infrastructure built on `structlog`. Provides pipeline configuration,
per-request context propagation, and ASGI middleware for automatic request/response logging.

## Files

| File | Description |
|---|---|
| `config.py` | `configure_logging()` — initialises the structlog processing pipeline |
| `context.py` | `ContextVar`-based request ID propagation |
| `middleware.py` | Three ASGI middlewares: `RequestIDMiddleware`, `RequestLoggingMiddleware`, `TimingMiddleware` |

---

## config.py

`configure_logging(log_level, use_json)` must be called once at application startup
(in `main.py`). It configures both the standard library `logging` module and `structlog`.

| Mode | Output format | When to use |
|---|---|---|
| `use_json=False` | Colourised console (dev) | Local development |
| `use_json=True` | JSON lines | Production / log aggregation (Datadog, ELK, etc.) |

---

## context.py

Manages request-scoped context using Python's `ContextVar`, which is safe in async
environments (each coroutine inherits a copy of the context from its parent).

```python
set_request_id(request_id)     # called by RequestIDMiddleware at request start
get_request_id() → str | None  # read by any code during request processing
get_logger_context() → dict    # {"request_id": "..."} spread into log calls
```

Usage in any class or function:
```python
import structlog
from ...infrastructure.logging.context import get_logger_context

logger = structlog.get_logger(__name__)
logger.info("Something happened", **get_logger_context())
```

---

## middleware.py

Three ASGI middlewares registered in `main.py`. Order matters — they run outermost-first:

### RequestIDMiddleware (outermost)
- Generates a UUID request ID via the injected `IdGenerator`.
- Stores it in `ContextVar` (via `set_request_id()`) and in `request.state.request_id`.
- Adds `X-Request-ID` to the response headers.

### RequestLoggingMiddleware
- Logs `"Request started"` with method, URL, path, query params, client IP, and user agent.
- Logs `"Request completed"` with status code.
- Logs `"Request failed"` with error details if an unhandled exception propagates.

### TimingMiddleware (innermost)
- Measures wall-clock time using the injected `TimeProvider`.
- Adds `X-Process-Time` (seconds as float) to response headers.
- Logs timing details at INFO level.

See `../README.md` for the full infrastructure layer overview.
