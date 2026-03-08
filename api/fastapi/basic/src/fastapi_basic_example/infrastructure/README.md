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
├── decorators/
│   └── logging.py           # @log_execution decorator
├── di/
│   └── dependencies.py      # FastAPI dependency factory functions
├── logging/
│   ├── config.py            # structlog initialisation
│   ├── context.py           # ContextVar-based request ID propagation
│   └── middleware.py        # ASGI middleware (request ID, logging, timing)
└── utils/
    ├── datetime_utils.py    # UTC timestamp helper
    ├── id_generator.py      # abstract ID generator + UUID implementation
    └── time_provider.py     # abstract time provider + system implementation
```

---

## config/settings.py

Application settings loaded from environment variables using Pydantic `BaseSettings`.

```python
class Settings(BaseSettings):
    app_name: str = AppConstants.APP_NAME
    app_version: str = AppConstants.APP_VERSION
    debug: bool = False
    reload: bool = False
    host: str = ServerConstants.DEFAULT_HOST
    port: int = ServerConstants.DEFAULT_PORT
    environment: str = "development"
    log_level: str = "INFO"
```

All fields have sensible defaults so the application starts without any environment
configuration. In production, set `ENVIRONMENT`, `LOG_LEVEL`, `HOST`, and `PORT` via
environment variables or a `.env` file (Pydantic `BaseSettings` reads both automatically).

---

## decorators/logging.py

`@log_execution(layer)` is a decorator that wraps any async function with structured
entry/exit log lines and elapsed-time measurement.

```python
@log_execution("use_cases")
async def execute(self, item_id: int, ...) -> ItemResponseDTO:
    ...
```

Log output includes:
- `layer` — the architectural layer name (e.g. `"use_cases"`)
- `function` — the decorated function's `__name__`
- `duration_ms` — elapsed time in milliseconds (on exit)
- `request_id` — propagated via `ContextVar` from the request context

Applied at the use-case layer to track every use-case invocation without modifying
use-case code.

---

## di/dependencies.py

FastAPI dependency factory functions. Each function is either called directly by FastAPI's
`Depends()` mechanism or injected into a route handler.

```python
def get_id_generator() -> IdGenerator: ...
def get_time_provider() -> TimeProvider: ...
def get_item_repository() -> ItemRepository: ...          # returns abstract port
def get_health_service() -> HealthService: ...
def get_item_use_case(
    repository: Annotated[ItemRepository, Depends(get_item_repository)],
) -> GetItemUseCase: ...
```

**Key principle:** factory functions return *abstract* types (`ItemRepository`,
`IdGenerator`, `TimeProvider`), never the concrete implementations. This means tests and
future adapters can swap the concrete class by overriding the factory via
`app.dependency_overrides` without changing any call site.

### Dependency graph

```
get_item_use_case
└── get_item_repository → InMemoryItemRepository (implements ItemRepository)

get_health_service → HealthService

get_id_generator → UuidGenerator (implements IdGenerator)
get_time_provider → SystemTimeProvider (implements TimeProvider)
```

---

## logging/config.py

Initialises `structlog` for the application. Call `configure_logging(settings)` once at
startup (in `main.py`) to set up the processing pipeline:

- Development: colourised console output, pretty-printed key=value pairs.
- Production: JSON lines suitable for log aggregation systems.

The log level is taken from `settings.log_level`.

---

## logging/context.py

Manages per-request context propagated through async call stacks using `ContextVar`.

```python
_request_id_var: ContextVar[str | None]

def set_request_id(request_id: str) -> None: ...
def get_request_id() -> str | None: ...
def get_logger_context() -> dict[str, str]: ...
```

`get_logger_context()` returns a dict ready to be spread into any `structlog` call:

```python
logger.info("Health service initialized", **get_logger_context())
# → {"event": "Health service initialized", "request_id": "abc-123"}
```

The `RequestIDMiddleware` sets the request ID at the start of each request; it is
automatically available to every log call downstream without passing it explicitly.

---

## logging/middleware.py

Three ASGI middlewares that run for every request:

| Middleware | Responsibility |
|---|---|
| `RequestIDMiddleware` | Generates or propagates `X-Request-ID`; sets the `ContextVar` |
| `RequestLoggingMiddleware` | Logs method, path, status code, and duration at request end |
| `TimingMiddleware` | Adds `X-Process-Time` response header (uses `TimeProvider`) |

They are registered in `main.py` in this order (outermost first):
`RequestIDMiddleware` → `RequestLoggingMiddleware` → `TimingMiddleware`.

---

## utils/datetime_utils.py

```python
def current_utc_timestamp() -> str:
    """Return the current UTC time as an ISO 8601 string."""
```

Used by `HealthService` and `create_probe_response()` in the router to stamp health
check responses. Isolated here so tests can monkeypatch a single location.

---

## utils/id_generator.py

Abstract ID generation with a UUID implementation.

```python
class IdGenerator(ABC):
    @abstractmethod
    def generate(self) -> str: ...

class UuidGenerator(IdGenerator):
    def generate(self) -> str:
        return str(uuid.uuid4())
```

Injected via `get_id_generator()` so tests can provide deterministic IDs.

---

## utils/time_provider.py

Abstract time retrieval with a system implementation.

```python
class TimeProvider(ABC):
    @abstractmethod
    def time(self) -> float: ...

class SystemTimeProvider(TimeProvider):
    def time(self) -> float:
        return time.time()
```

Used by `TimingMiddleware` to measure request duration. The abstraction allows tests to
inject a fixed time and assert on `X-Process-Time` header values.
