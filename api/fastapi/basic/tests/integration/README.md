# tests/integration

Integration tests that verify multiple real components work correctly together. Unlike unit
tests, these start a real `FastAPI` application instance and exercise the DI container.
Unlike e2e tests, individual collaborators can be swapped via `app.dependency_overrides`
to control behaviour without relying on real storage state.

All test classes are marked `@pytest.mark.integration`.

---

## Test files

| File | What it tests |
|---|---|
| `test_api_with_di.py` | HTTP endpoints with selectively mocked dependencies |
| `test_repository_integration.py` | `InMemoryItemRepository` wired through the full DI graph |

---

## test_api_with_di.py

Demonstrates FastAPI's `dependency_overrides` pattern for replacing services with mocks
mid-test:

```python
app.dependency_overrides[get_health_service] = lambda: mock_health_service
response = client.get("/health")
app.dependency_overrides.clear()
```

Tests in this file cover:
- Root endpoint returns `{"Hello": "World"}` without any mocking needed.
- Health endpoint returns the mock's `HealthCheckDTO`.
- Liveness probe returns `{"status": "alive"}` when mock `is_alive()` returns `True`.
- Readiness probe returns HTTP 503 when mock `is_ready()` returns `False`.
- Items endpoint calls `GetItemUseCase.execute()` and maps the result to JSON.

---

## test_repository_integration.py

Tests `InMemoryItemRepository` as a black box: save an item, retrieve it, delete it, verify
not-found behaviour. These tests use the real repository without mocking, confirming that
the port contract (`ItemRepository` abstract methods) is correctly implemented.

---

## Conventions

- `app` and `client` fixtures are injected from `tests/conftest.py`.
- `dependency_overrides` are always cleared in a `finally`-equivalent step after the
  assertion, so leaked overrides cannot affect subsequent tests.
- Async tests use `@pytest.mark.asyncio`; the event loop scope is per-function (default).
