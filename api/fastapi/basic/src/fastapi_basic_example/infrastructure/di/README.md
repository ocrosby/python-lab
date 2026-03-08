# infrastructure/di

Dependency injection wiring. This is the only place in the codebase where abstract ports
are bound to concrete adapter implementations.

## Files

| File | Description |
|---|---|
| `dependencies.py` | FastAPI `Depends()`-compatible factory functions |

## Factory functions

| Function | Return type | Concrete class created |
|---|---|---|
| `get_id_generator()` | `IdGenerator` | `UuidGenerator` |
| `get_time_provider()` | `TimeProvider` | `SystemTimeProvider` |
| `get_item_repository()` | `ItemRepository` | `InMemoryItemRepository` |
| `get_health_service()` | `HealthService` | `HealthService` |
| `get_item_use_case(repository)` | `GetItemUseCase` | `GetItemUseCase` |

All functions return **abstract** types (ports or service classes), never the concrete
implementation type. This allows tests and future environments to override a single factory
without touching any call site.

## Dependency graph

```
get_item_use_case
└── get_item_repository → InMemoryItemRepository (satisfies ItemRepository)

get_health_service → HealthService

get_id_generator → UuidGenerator (satisfies IdGenerator)
get_time_provider → SystemTimeProvider (satisfies TimeProvider)
```

## Overriding in tests

FastAPI's `app.dependency_overrides` mechanism maps a factory function to a replacement:

```python
app.dependency_overrides[get_health_service] = lambda: mock_health_service
response = client.get("/health")
app.dependency_overrides.clear()
```

This is the standard pattern used in `tests/integration/test_api_with_di.py`.

## Swapping an adapter (e.g. real database)

1. Create the new adapter in `adapters/outbound/persistence/`.
2. Update the relevant factory function here to return the new concrete class.
3. No other files change.

See `../README.md` for the full infrastructure layer overview.
