# fastapi_basic_example

The root package of the application. It wires all architectural layers together via
`main.py` and exposes the `app` object consumed by the ASGI server (uvicorn).

---

## Architecture overview

This application follows **Hexagonal Architecture** (also called Ports and Adapters). The
goal is to keep the business core completely independent of frameworks, databases, and
external protocols.

```
┌─────────────────────────────────────────────────────────┐
│                    adapters/inbound                      │
│                  (HTTP — FastAPI routes)                 │
└──────────────────────┬──────────────────────────────────┘
                       │ calls
┌──────────────────────▼──────────────────────────────────┐
│                    application/                          │
│              (use cases, services, DTOs)                 │
└──────────────────────┬──────────────────────────────────┘
                       │ depends on
┌──────────────────────▼──────────────────────────────────┐
│                      domain/                             │
│         (entities, value objects, errors, constants)     │
└─────────────────────────────────────────────────────────┘
                       ▲ implements
┌──────────────────────┴──────────────────────────────────┐
│                      ports/                              │
│               (abstract interfaces / contracts)          │
└──────────────────────▲──────────────────────────────────┘
                       │ implements
┌──────────────────────┴──────────────────────────────────┐
│                  adapters/outbound                       │
│              (in-memory persistence, etc.)               │
└─────────────────────────────────────────────────────────┘
                  infrastructure/
            (config, logging, DI, utilities)
                  (used by all layers)
```

**Dependency rule:** arrows always point inward. Outer layers know about inner layers;
inner layers never import from outer layers.

---

## Package layout

```
fastapi_basic_example/
├── main.py               # application factory + ASGI entry point
├── adapters/             # concrete inbound and outbound implementations
├── application/          # use cases, services, DTOs
├── domain/               # pure business model
├── infrastructure/       # cross-cutting concerns (config, logging, DI, utils)
└── ports/                # abstract interfaces (contracts)
```

Each sub-package contains its own `README.md` with detailed documentation.

---

## main.py

`create_app()` is the application factory. It:

1. Loads `Settings` from environment variables / `.env`.
2. Calls `configure_logging()` to initialise `structlog`.
3. Creates the `FastAPI` instance with title, description, and version from `AppConstants`.
4. Registers middleware in outermost-first order:
   - `TrustedHostMiddleware` — rejects requests from unknown hosts
   - `CORSMiddleware` — cross-origin resource sharing policy
   - `GZipMiddleware` — response compression
   - `TimingMiddleware` — adds `X-Process-Time` header
   - `RequestLoggingMiddleware` — logs every request and response
   - `RequestIDMiddleware` — generates/propagates `X-Request-ID`
5. Includes the router from `adapters/inbound/http/routers.py`.

The module-level `app = create_app()` is the object uvicorn targets:

```bash
uvicorn src.fastapi_basic_example.main:app --reload
```

---

## Quick start

```bash
# Install dependencies
uv sync

# Run development server
uv run uvicorn src.fastapi_basic_example.main:app --reload

# Run tests
uv run pytest tests/

# Lint / format
uv run ruff check .
uv run ruff format .
```
