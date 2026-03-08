# CLAUDE.md — fastapi-oauth-example

This file is read automatically by Claude Code at the start of every session.

---

## Project summary

A FastAPI reference implementation demonstrating **OAuth2 JWT authentication** with
PostgreSQL, hexagonal architecture, security features (rate limiting, account lockout,
MFA, token blacklisting), and Kubernetes health probes.

**Package:** `src/fastapi_oauth_example/`
**Entry point:** `src/fastapi_oauth_example/main.py` → `app` (FastAPI instance)
**Package manager:** `uv`
**Linter/formatter:** `ruff`
**Test runner:** `pytest` with `pytest-asyncio`

---

## Architecture

```
domain/                  ← entities, value objects, repositories (pure business logic)
application/             ← use cases, services, DTOs (orchestration)
infrastructure/
  config/                ← settings (pydantic-settings)
  di/                    ← dependency injection wiring
  persistence/           ← SQLAlchemy models, database, repository implementations
  security/              ← JWT, password hashing, rate limiter, MFA, audit logger
  web/                   ← FastAPI routers and middleware
```

**Dependency rule:** imports always point inward. `infrastructure/web/` → `application/`
→ `domain/`. `infrastructure/` is used by all layers but depends only on third-party libs.

---

## Key conventions

- **Repositories** (`domain/repositories/`) are abstract base classes (`ABC`). Factory
  functions in `infrastructure/di/dependencies.py` return the **abstract** type.
- **Use cases** accept repositories and services as constructor args; they never import
  from `infrastructure/web/`.
- **DTOs** (`application/dto/user_dto.py`) are Pydantic `BaseModel` subclasses. They are
  the only types that cross the web ↔ application boundary.
- **Async tests** use `@pytest.mark.asyncio`; repository methods are mocked with `AsyncMock`.
- **Dependency overrides** in tests use `app.dependency_overrides[factory_fn] = lambda: mock`
  and are cleared immediately after the response is received.

---

## Common commands

```bash
# Run all tests
uv run pytest tests/

# Run with coverage
uv run pytest tests/ --cov

# Run only unit tests
uv run pytest tests/unit/

# Lint
uv run ruff check .

# Format
uv run ruff format .

# Start dev server
uv run uvicorn src.fastapi_oauth_example.main:app --reload

# Type check
uv run mypy src/

# Security scan (SAST)
uv run bandit -r src/ -ll

# Dependency vulnerability scan
uv run pip-audit
```

---

## Important files

| File | Purpose |
|---|---|
| `src/fastapi_oauth_example/main.py` | App instance, middleware registration, router inclusion |
| `src/fastapi_oauth_example/infrastructure/web/auth_router.py` | Auth HTTP route handlers |
| `src/fastapi_oauth_example/infrastructure/web/health_router.py` | Health probe handlers |
| `src/fastapi_oauth_example/infrastructure/di/dependencies.py` | DI wiring (only place that touches concrete implementations) |
| `src/fastapi_oauth_example/domain/repositories/user_repository.py` | User storage port contract |
| `src/fastapi_oauth_example/infrastructure/config/settings.py` | All app configuration |
| `pyproject.toml` | All tool configuration (pytest, ruff, coverage) |

---

## Code quality standards

- **DRY/SOLID/CLEAN** principles must be maintained at all times.
- **Cyclomatic complexity ≤ 7** for every function and method. Refactor by extracting
  helpers or simplifying branching before committing if this limit is exceeded.

---

## Pytest markers

| Marker | Meaning |
|---|---|
| `unit` | Isolated, no I/O, fast |
| `integration` | Multiple real components, uses `dependency_overrides` |
| `e2e` | Full HTTP round-trip via `TestClient` |
