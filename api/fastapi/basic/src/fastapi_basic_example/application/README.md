# application

The **application** package orchestrates the domain. It sits between the domain (what the
business rules are) and the adapters (how the outside world interacts). It is the layer
that knows *what to do* but not *how* infrastructure works.

Dependencies allowed from this layer:
- `domain/` — entities, errors, constants, value objects
- `ports/` — abstract repository and service contracts
- `infrastructure/` — only cross-cutting concerns (logging decorators, DI annotations)

Dependencies **not** allowed:
- `adapters/` — no concrete HTTP, persistence, or messaging code
- FastAPI request/response types — DTOs are plain Pydantic models, not `Request`/`Response`

---

## Package layout

```
application/
├── dto/
│   └── item_dto.py          # data transfer objects (Pydantic models)
├── services/
│   └── health_service.py    # health / probe business logic
└── use_cases/
    └── get_item_use_case.py # single use case: fetch an item by ID
```

---

## dto/item_dto.py

Data Transfer Objects are the shapes of data crossing the boundary between the application
core and adapters. They are Pydantic `BaseModel` subclasses, which provides automatic
validation and JSON serialisation.

| DTO | Fields | Purpose |
|---|---|---|
| `ItemResponseDTO` | `item_id: int`, `q: str \| None` | Response for `GET /items/{id}` |
| `HealthCheckDTO` | `status: str`, `timestamp: str` | Response for `GET /health` |
| `WelcomeDTO` | `Hello: str = "World"` | Response for `GET /` |
| `ProbeResponseDTO` | `status: str`, `timestamp: str` | Response for liveness / readiness / startup probes |

DTOs are **not** domain entities. They exist to decouple the wire format from internal
domain objects. If the API shape needs to change (e.g. rename a field, add versioning),
only the DTO and its mapping code change — the domain entity is unaffected.

---

## services/health_service.py

`HealthService` encapsulates the logic for answering the three standard Kubernetes health
questions. It has no dependency on the HTTP layer; routers call it through DI.

```python
class HealthService:
    def get_health_status(self) -> HealthCheckDTO: ...
    async def is_alive(self) -> bool: ...
    async def is_ready(self) -> bool: ...
```

| Method | Used by | Meaning |
|---|---|---|
| `get_health_status()` | `GET /health` | Returns current status + timestamp |
| `is_alive()` | `GET /health/live`, `GET /health/startup` | Is the process running? |
| `is_ready()` | `GET /health/ready` | Is the process ready to accept traffic? |

Both async methods currently return `True` unconditionally. To add real readiness checks
(e.g. database connectivity, cache warm-up), replace the `return True` bodies with
appropriate checks. The probe routes in `adapters/inbound/http/routers.py` handle the
`False` case by raising `HTTP 503`.

---

## use_cases/get_item_use_case.py

`GetItemUseCase` is the single application use case. It coordinates between the inbound
request (item ID + optional query params) and the outbound `ItemRepository` port.

```python
class GetItemUseCase:
    def __init__(self, item_repository: ItemRepository): ...

    @log_execution("use_cases")
    async def execute(
        self,
        item_id: int,
        query_params: QueryParams | None = None,
    ) -> ItemResponseDTO: ...
```

### Behaviour

1. Calls `item_repository.get_by_id(item_id)`.
2. If the result is `None`, raises `ItemNotFoundError(item_id=item_id)`.
3. Maps the domain `Item` entity to `ItemResponseDTO` and returns it.

The `@log_execution` decorator (from `infrastructure/decorators/logging.py`) automatically
logs entry, exit, and duration without cluttering the use-case logic.

### Dependency injection

`GetItemUseCase` depends on `ItemRepository` (the port abstraction), not on
`InMemoryItemRepository` (the concrete adapter). The concrete adapter is wired in
`infrastructure/di/dependencies.py`, keeping the use case agnostic of storage details.

---

## Adding a new use case

1. Create `application/use_cases/<verb>_<noun>_use_case.py`.
2. Accept ports (from `ports/`) as constructor arguments — never concrete adapters.
3. Return a DTO from `application/dto/`.
4. Raise domain errors from `domain/errors.py` for expected failure conditions.
5. Add a factory function in `infrastructure/di/dependencies.py`.
6. Inject via `Annotated[MyUseCase, Depends(get_my_use_case)]` in the router.
