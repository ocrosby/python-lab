# application/dto

Data Transfer Objects (DTOs) define the shapes of data that cross the boundary between the
application core and its adapters. They are Pydantic `BaseModel` subclasses, providing
automatic validation and JSON serialisation.

## Files

| File | DTOs |
|---|---|
| `item_dto.py` | `ItemResponseDTO`, `HealthCheckDTO`, `WelcomeDTO`, `ProbeResponseDTO` |

## DTOs

### ItemResponseDTO
Response shape for `GET /items/{item_id}`.
```python
class ItemResponseDTO(BaseModel):
    item_id: int   # must be > 0
    q: str | None
```

### HealthCheckDTO
Response shape for `GET /health`.
```python
class HealthCheckDTO(BaseModel):
    status: str      # e.g. "healthy"
    timestamp: str   # ISO 8601 UTC string
```

### WelcomeDTO
Response shape for `GET /`.
```python
class WelcomeDTO(BaseModel):
    Hello: str = "World"
```

### ProbeResponseDTO
Response shape for liveness, readiness, and startup probe endpoints.
```python
class ProbeResponseDTO(BaseModel):
    status: str      # "alive" | "ready" | "started"
    timestamp: str   # ISO 8601 UTC string
```

## Design notes

- DTOs are **not** domain entities. They exist to decouple wire format from internal
  domain model. Changing an API field name does not require touching `domain/entities/`.
- DTOs should not contain business logic. Validation is limited to structural rules
  (e.g. `item_id > 0`), not domain invariants.

See `../README.md` for the full application layer overview.
