# tests/unit

Unit tests for individual classes and functions in isolation. No network calls, no ASGI
startup, no filesystem access. External collaborators are replaced with `MagicMock` or
`AsyncMock` where needed.

All test classes are marked `@pytest.mark.unit`.

---

## Test files

| File | What it tests |
|---|---|
| `test_dtos.py` | Pydantic DTO construction, field defaults, validation |
| `test_entities.py` | `Item` entity — field validation, frozen immutability |
| `test_errors.py` | `DomainError`, `ItemNotFoundError`, `ValidationError` — exception hierarchy, attributes |
| `test_get_item_use_case.py` | `GetItemUseCase.execute()` — found item, not-found → `ItemNotFoundError`, query param forwarding |
| `test_health_service.py` | `HealthService` — `get_health_status()`, `is_alive()`, `is_ready()` |
| `test_item_repository.py` | `InMemoryItemRepository` — `get_by_id`, `save`, `delete`, not-found cases |
| `test_logging_config.py` | `configure_logging()` — structlog pipeline for dev and JSON modes |
| `test_logging_decorator.py` | `@log_execution` — logs entry/exit/errors for async and sync functions |
| `test_logging_middleware.py` | `RequestIDMiddleware`, `RequestLoggingMiddleware`, `TimingMiddleware` |
| `test_result.py` | `Success`, `Failure`, `Result` type — `is_success()`, `is_failure()`, immutability |
| `test_settings.py` | `Settings` — defaults, env var overrides, validators (port range, log level) |
| `test_value_objects.py` | `QueryParams` — empty string normalisation, frozen immutability |

---

## Conventions

- One test class per production class, named `Test<ClassName>`.
- Each test method covers a single behaviour, named `test_<what_and_expected_outcome>`.
- `AsyncMock` is used for async repository methods injected into use cases.
- `pytest-mock`'s `mocker` fixture is used instead of `unittest.mock.patch` where possible.
