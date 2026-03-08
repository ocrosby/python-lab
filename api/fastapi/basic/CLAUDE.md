# CLAUDE.md — fastapi-basic-example

This file is read automatically by Claude Code at the start of every session.

---

## Project summary

A FastAPI reference implementation demonstrating **Hexagonal Architecture** (Ports and
Adapters) with structured logging, dependency injection, and Kubernetes health probes.

**Package:** `src/fastapi_basic_example/`
**Entry point:** `src/fastapi_basic_example/main.py` → `app = create_app()`
**Package manager:** `uv`
**Linter/formatter:** `ruff`
**Test runner:** `pytest` with `pytest-asyncio`

---

## Architecture

```
adapters/inbound/http/   ← FastAPI routes (HTTP driving adapter)
application/             ← use cases, services, DTOs (orchestration)
domain/                  ← entities, value objects, errors, constants (pure business logic)
ports/outbound/          ← abstract interfaces owned by the application core
adapters/outbound/       ← concrete implementations (storage, etc.)
infrastructure/          ← config, logging, DI, utils (cross-cutting concerns)
```

**Dependency rule:** imports always point inward. `adapters/` → `application/` → `domain/`.
`infrastructure/` is used by all layers but depends only on third-party libs.

---

## Key conventions

- **Ports** (`ports/outbound/`) are abstract base classes (`ABC`). Factory functions in
  `infrastructure/di/dependencies.py` return the **abstract** type, never the concrete class.
- **Use cases** accept ports as constructor args; they never import from `adapters/`.
- **Domain errors** (`domain/errors.py`) inherit from `Exception` via `DomainError`.
  Route handlers in `routers.py` catch them and map to HTTP status codes.
- **DTOs** (`application/dto/item_dto.py`) are Pydantic `BaseModel` subclasses. They are
  the only types that cross the adapter ↔ application boundary.
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
uv run uvicorn src.fastapi_basic_example.main:app --reload
```

---

## Important files

| File | Purpose |
|---|---|
| `src/fastapi_basic_example/main.py` | App factory, middleware registration |
| `src/fastapi_basic_example/adapters/inbound/http/routers.py` | All HTTP route handlers |
| `src/fastapi_basic_example/infrastructure/di/dependencies.py` | DI wiring (only place that touches concrete adapters) |
| `src/fastapi_basic_example/ports/outbound/item_repository.py` | Storage port contract |
| `src/fastapi_basic_example/domain/errors.py` | Domain exception hierarchy |
| `tests/conftest.py` | Shared fixtures: `app`, `client`, `seeded_client` |
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
