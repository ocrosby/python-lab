# tests

The test suite for `fastapi_basic_example`. Tests are organised into three layers that
mirror the test pyramid: many unit tests, fewer integration tests, and a small number of
end-to-end tests.

---

## Layout

```
tests/
├── conftest.py        # shared fixtures (app, client, seeded_client)
├── unit/              # fast, isolated, no I/O
├── integration/       # tests interactions between layers
└── e2e/               # full HTTP request/response through the live app
```

---

## Running tests

```bash
# All tests
uv run pytest tests/

# Stop at first failure
uv run pytest tests/ -x

# Specific layer
uv run pytest tests/unit/
uv run pytest tests/integration/
uv run pytest tests/e2e/

# By marker
uv run pytest -m unit
uv run pytest -m integration
uv run pytest -m e2e

# With verbose output
uv run pytest tests/ -v

# Coverage report (configured in pyproject.toml)
uv run pytest tests/ --cov
```

---

## Pytest markers

Markers are declared in `pyproject.toml` and applied via class- or function-level
decorators.

| Marker | Meaning |
|---|---|
| `unit` | Pure unit tests — no network, no disk, no framework startup |
| `integration` | Tests that wire multiple real components together |
| `e2e` | Full HTTP round-trips via `TestClient` |
| `asyncio` | Async test function (handled automatically by `pytest-asyncio`) |

---

## Shared fixtures (`conftest.py`)

| Fixture | Scope | Description |
|---|---|---|
| `app` | function | Fresh `FastAPI` instance from `create_app()` |
| `client` | function | `TestClient` wrapping `app` |
| `seeded_client` | function | `TestClient` with `InMemoryItemRepository` pre-populated via `dependency_overrides` |

`seeded_client` is used by e2e tests that exercise the items endpoint — it pre-saves an
`Item(item_id=1)` so `GET /items/1` returns 200 without requiring a real database.

---

## Coverage

The project is configured to require **80% minimum** coverage. Actual coverage is
currently ~99.7%. The coverage report is written to `htmlcov/` (HTML) and `coverage.xml`
(for CI tools).
