# adapters

The **adapters** package contains the concrete implementations that connect the application
core to the outside world. Adapters translate between the application's internal language
(domain entities, DTOs, ports) and external protocols and storage formats.

In hexagonal architecture terminology:
- **Inbound adapters** translate external calls *into* the application (HTTP → use case).
- **Outbound adapters** translate application calls *out to* external systems (port → storage).

Adapters are allowed to depend on infrastructure libraries (FastAPI, SQLAlchemy, etc.).
The application core must not import from this package.

---

## Package layout

```
adapters/
├── inbound/
│   └── http/
│       ├── auth_router.py      # FastAPI auth route handlers
│       └── health_router.py    # FastAPI health probe handlers
└── outbound/
    └── persistence/
        ├── database.py                   # SQLAlchemy async engine / session factory
        ├── models.py                     # SQLAlchemy ORM models
        ├── postgres_user_repository.py   # PostgresUserRepository (implements UserRepository)
        └── token_repositories.py        # token/session repository implementations
```

---

## inbound/http/

The HTTP inbound adapters. Each route handler is a thin translation layer:
1. Receive a FastAPI `Request` (via path/query parameters and DI).
2. Call the appropriate use case or service.
3. Return a DTO (FastAPI serialises it to JSON).

Route handlers contain no business logic. Error handling maps domain errors to HTTP
status codes.

---

## outbound/persistence/

PostgreSQL persistence adapters that implement ports from `ports/outbound/`.

`PostgresUserRepository` implements the `UserRepository` port using SQLAlchemy async ORM.
Because the DI container returns `UserRepository` (the port abstraction), replacing this
with a different storage backend requires only a new class and a one-line change in
`infrastructure/di/dependencies.py`.

---

## Adding a new adapter

**New HTTP endpoint:** add a route to an existing router in `inbound/http/` or create a
new router and register it in `main.py`.

**New outbound adapter (e.g. Redis cache):**
1. Create `adapters/outbound/<category>/<impl>.py` implementing the relevant port.
2. Register it in `infrastructure/di/dependencies.py`.
