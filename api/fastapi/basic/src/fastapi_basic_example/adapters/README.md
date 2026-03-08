# adapters

The **adapters** package contains the concrete implementations that connect the application
core to the outside world. Adapters translate between the application's internal language
(domain entities, DTOs, ports) and external protocols and storage formats.

In hexagonal architecture terminology:
- **Inbound adapters** translate external calls *into* the application (HTTP → use case).
- **Outbound adapters** translate application calls *out to* external systems (port → storage).

Adapters are allowed to depend on infrastructure libraries (FastAPI, databases, HTTP
clients). The application core must not import from this package.

---

## Package layout

```
adapters/
├── inbound/
│   └── http/
│       └── routers.py          # FastAPI route handlers (HTTP inbound adapter)
└── outbound/
    └── persistence/
        └── in_memory_item_repository.py   # in-memory storage (outbound adapter)
```

---

## inbound/http/routers.py

The HTTP inbound adapter. Each route handler is a thin translation layer:
1. Receive a FastAPI `Request` (via path/query parameters and DI).
2. Call the appropriate use case or service.
3. Return a DTO (FastAPI serialises it to JSON).

Route handlers do not contain business logic. Error handling maps domain errors to HTTP
status codes.

### Registered routes

| Method | Path | Handler | Description |
|---|---|---|---|
| `GET` | `/` | `read_root` | Returns `{"Hello": "World"}` |
| `GET` | `/items/{item_id}` | `read_item` | Fetch item by ID; 404 if not found |
| `GET` | `/health` | `health_check` | Current health status + timestamp |
| `GET` | `/health/live` | `liveness_probe` | Kubernetes liveness probe (also `/healthz`) |
| `GET` | `/health/ready` | `readiness_probe` | Kubernetes readiness probe (also `/readiness`) |
| `GET` | `/health/startup` | `startup_probe` | Kubernetes startup probe |

The `/healthz` and `/readiness` paths are aliased via a second `@router.get` decorator
with `include_in_schema=False` so they appear in Kubernetes manifests but not in the
OpenAPI docs.

### Dependency injection pattern

Route handlers declare their dependencies using FastAPI's `Depends()`:

```python
@router.get("/items/{item_id}", response_model=ItemResponseDTO)
async def read_item(
    item_id: int,
    q: str | None = None,
    *,
    use_case: Annotated[GetItemUseCase, Depends(get_item_use_case)],
) -> ItemResponseDTO:
    query_params = QueryParams(q=q) if q is not None else None
    try:
        return await use_case.execute(item_id, query_params)
    except ItemNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
```

The router imports only from `application/` and `ports/`; it has no knowledge of
`infrastructure/persistence/` or any concrete adapter.

### Error mapping

| Domain error | HTTP status | Detail |
|---|---|---|
| `ItemNotFoundError` | `404 Not Found` | `str(e)` → `"Item {id} not found"` |
| Service not alive | `503 Service Unavailable` | `"Service not alive"` |
| Service not ready | `503 Service Unavailable` | `"Service not ready"` |
| Service not started | `503 Service Unavailable` | `"Service not started"` |

---

## outbound/persistence/in_memory_item_repository.py

The in-memory outbound adapter. Implements `ItemRepository` (from `ports/outbound/`) using
a plain Python dictionary as the backing store.

```python
class InMemoryItemRepository(ItemRepository):
    def __init__(self):
        self._store: dict[int, Item] = {}

    async def get_by_id(self, item_id: int) -> Item | None: ...
    async def save(self, item: Item) -> Item: ...
    async def delete(self, item_id: int) -> bool: ...
```

This adapter is suitable for development, testing, and demos. Because the DI container
returns `ItemRepository` (the port abstraction), replacing this with a SQL or Redis adapter
requires only a new class in `adapters/outbound/persistence/` and a one-line change in
`infrastructure/di/dependencies.py`.

### Replacing the adapter

1. Create `adapters/outbound/persistence/<new_adapter>.py` implementing `ItemRepository`.
2. In `infrastructure/di/dependencies.py`, change `get_item_repository()` to return an
   instance of the new adapter.
3. No other files need to change.

---

## Adding a new adapter

**New HTTP endpoint:** add a route to `inbound/http/routers.py` (or create a new router
and register it in `main.py`).

**New outbound adapter (e.g. Redis cache):**
1. Create `adapters/outbound/<category>/<impl>.py` implementing the relevant port.
2. Register it in `infrastructure/di/dependencies.py`.
