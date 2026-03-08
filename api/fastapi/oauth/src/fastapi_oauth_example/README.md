# fastapi_oauth_example

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
│         (entities, value objects)                        │
└─────────────────────────────────────────────────────────┘
                       ▲ implements
┌──────────────────────┴──────────────────────────────────┐
│                      ports/                              │
│               (abstract interfaces / contracts)          │
└──────────────────────▲──────────────────────────────────┘
                       │ implements
┌──────────────────────┴──────────────────────────────────┐
│                  adapters/outbound                       │
│              (PostgreSQL persistence)                    │
└─────────────────────────────────────────────────────────┘
                  infrastructure/
            (config, logging, DI, security)
                  (used by all layers)
```

**Dependency rule:** arrows always point inward. Outer layers know about inner layers;
inner layers never import from outer layers.

---

## Package layout

```
fastapi_oauth_example/
├── main.py               # application entry point
├── adapters/             # concrete inbound and outbound implementations
├── application/          # use cases, services, DTOs
├── domain/               # pure business model
├── infrastructure/       # cross-cutting concerns (config, logging, DI, security)
└── ports/                # abstract interfaces (contracts)
```

Each sub-package contains its own `README.md` with detailed documentation.

---

## main.py

Configures the `FastAPI` instance. It:

1. Loads `Settings` from environment variables / `.env`.
2. Creates the `FastAPI` instance with title, description, version, and docs URLs.
3. Initialises the database via the lifespan context manager.
4. Registers middleware in outermost-first order:
   - `TrustedHostMiddleware` — rejects requests from unknown hosts
   - `CORSMiddleware` — cross-origin resource sharing policy
   - `GZipMiddleware` — response compression
   - `RateLimitMiddleware` — per-IP request rate limiting
   - `SecurityHeadersMiddleware` — sets security response headers
   - `TimingMiddleware` — adds `X-Process-Time` header
   - `LoggingMiddleware` — logs every request and response
   - `RequestIDMiddleware` — generates/propagates `X-Request-ID`
5. Includes the auth and health routers from `adapters/inbound/http/`.

The module-level `app` is the object uvicorn targets:

```bash
uvicorn src.fastapi_oauth_example.main:app --reload
```

---

## Quick start

```bash
# Install dependencies
uv sync

# Run development server
uv run uvicorn src.fastapi_oauth_example.main:app --reload

# Run tests
uv run pytest tests/

# Lint / format
uv run ruff check .
uv run ruff format .
```
