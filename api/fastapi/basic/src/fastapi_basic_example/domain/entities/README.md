# domain/entities

Domain entities are the core business objects. They are identified by a unique ID and
encapsulate business invariants through field validators.

Entities in this project are frozen Pydantic `BaseModel` subclasses. Using Pydantic
provides built-in validation while keeping entities framework-agnostic — they have no
dependency on FastAPI, SQLAlchemy, or any persistence technology.

## Files

| File | Class | Description |
|---|---|---|
| `item.py` | `Item` | Central business entity — represents a managed item |

## Item

```python
class Item(BaseModel):
    model_config = ConfigDict(frozen=True, str_strip_whitespace=True)

    item_id: int          # positive, required
    name: str | None      # optional; empty string → validation error
    description: str | None  # optional; whitespace stripped to None
```

**Invariants enforced by validators:**
- `item_id` must be greater than 0.
- `name`, if provided, must not be blank (whitespace-only raises `ValueError`).
- `name` and `description` have leading/trailing whitespace stripped automatically.

**Frozen:** once constructed, an `Item` cannot be mutated. To update an item, construct a
new instance (use Pydantic's `model_copy(update={...})`).

## Adding a new entity

1. Create `domain/entities/<name>.py` with a frozen `BaseModel` subclass.
2. Define only the fields and validators that enforce domain invariants.
3. Add the corresponding repository port in `ports/outbound/<name>_repository.py`.
4. Implement the repository in `adapters/outbound/persistence/`.

See `../README.md` for the full domain layer overview.
