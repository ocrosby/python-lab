# tests/e2e

End-to-end tests that exercise the full HTTP request/response cycle with a real running
application instance. No mocking — the DI container resolves all dependencies as it would
in production, except that `InMemoryItemRepository` is used instead of a real database
(pre-seeded via `dependency_overrides` where needed).

All test classes are marked `@pytest.mark.e2e`.

---

## Test files

| File | What it tests |
|---|---|
| `test_api.py` | Happy-path HTTP responses for all major endpoints |
| `test_probe_failures.py` | HTTP 503 responses when health checks fail |

---

## test_api.py

Uses the `seeded_client` fixture (from `tests/conftest.py`) which pre-populates the
in-memory repository with `Item(item_id=1)` before the test client is created.

| Test | Endpoint | Expected |
|---|---|---|
| `test_read_root` | `GET /` | 200 `{"Hello": "World"}` |
| `test_read_item` | `GET /items/1` | 200 `{"item_id": 1, ...}` |
| `test_read_item_not_found` | `GET /items/999` | 404 |
| `test_health_check` | `GET /health` | 200 `{"status": "healthy", ...}` |
| `test_liveness_probe` | `GET /health/live` | 200 `{"status": "alive", ...}` |
| `test_readiness_probe` | `GET /health/ready` | 200 `{"status": "ready", ...}` |
| `test_startup_probe` | `GET /health/startup` | 200 `{"status": "started", ...}` |

---

## test_probe_failures.py

Uses `dependency_overrides` to inject a `HealthService` whose async methods return `False`,
confirming that the probe routes respond with HTTP 503 and a descriptive detail message.

| Test | Endpoint | Condition | Expected |
|---|---|---|---|
| `test_liveness_probe_failure` | `GET /health/live` | `is_alive()` → `False` | 503 `"Service not alive"` |
| `test_readiness_probe_failure` | `GET /health/ready` | `is_ready()` → `False` | 503 `"Service not ready"` |
| `test_startup_probe_failure` | `GET /health/startup` | `is_alive()` → `False` | 503 `"Service not started"` |
| `test_healthz_alias` | `GET /healthz` | `is_alive()` → `False` | 503 |
| `test_readiness_alias` | `GET /readiness` | `is_ready()` → `False` | 503 |

---

## Conventions

- E2e tests use the standard `client` or `seeded_client` fixture — never call
  `TestClient` directly inside a test.
- `dependency_overrides` are cleared immediately after the response is received, before
  assertions, to keep test isolation tight.
- E2e tests should not assert on internal implementation details (log output, call counts).
  Assert only on the HTTP response status and body.
