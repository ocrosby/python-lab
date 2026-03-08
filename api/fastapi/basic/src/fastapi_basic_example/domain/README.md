# domain

The **domain** package is the innermost layer of the hexagonal architecture. It contains
pure business concepts with no dependencies on any framework, database, HTTP library, or
other infrastructure concern. Everything here can be understood, instantiated, and tested
without importing FastAPI, SQLAlchemy, or any other external package.

---

## Package layout

```
domain/
├── constants.py          # named constants shared across layers
├── errors.py             # domain-specific exception hierarchy
├── result.py             # generic Result type (Success / Failure)
├── entities/
│   └── item.py           # Item entity
└── value_objects/
    └── query_params.py   # QueryParams value object
```

---

## constants.py

Defines three frozen constant classes that provide named values used across the codebase.
Keeping magic strings here prevents them from being scattered through routers, services, and tests.

| Class | Constants |
|---|---|
| `AppConstants` | `APP_NAME`, `APP_VERSION` |
| `HealthConstants` | `HEALTHY`, `ALIVE`, `READY`, `STARTED` |
| `ServerConstants` | `DEFAULT_HOST`, `DEFAULT_PORT` |

---

## errors.py

Domain-specific exception hierarchy. All domain errors inherit from `DomainError`, which
itself inherits from `Exception`, so they integrate naturally with Python's exception
machinery and FastAPI's `HTTPException` handler pattern.

```
Exception
└── DomainError(message: str)
    ├── ItemNotFoundError(item_id: int)   → "Item {id} not found"
    └── ValidationError(field: str)       → "Validation failed for field: {field}"
```

Errors carry structured data (`item_id`, `field`) as attributes so callers can log or
respond with machine-readable context, not just a string message.

---

## result.py

A generic `Result` type inspired by Rust's `Result<T, E>` and Haskell's `Either`.

```python
Result[T, E] = Success[T] | Failure[E]
```

| Type | Attribute | `is_success()` | `is_failure()` |
|---|---|---|---|
| `Success[T]` | `.value: T` | `True` | `False` |
| `Failure[E]` | `.error: E` | `False` | `True` |

Both are frozen dataclasses so they are immutable once created. This type is available for
use cases and services that prefer returning values over raising exceptions (e.g. validation
pipelines). The current use-case layer uses the exception-based flow, but `Result` is
retained for future adopters.

---

## entities/item.py

`Item` is the central domain entity. It encapsulates the identity and state of an item
managed by the application.

```python
@dataclass
class Item:
    item_id: int
    q: str | None = None
```

Entities are identified by their `item_id`. They are plain dataclasses — no Pydantic, no
ORM annotations.

---

## value_objects/query_params.py

`QueryParams` is a frozen Pydantic `BaseModel` that wraps the optional query string
parameter accepted by the items endpoint. It is a value object: equality is based on its
fields, not identity.

```python
class QueryParams(BaseModel):
    model_config = ConfigDict(frozen=True)
    q: str | None = None
```

A `field_validator` normalises empty strings to `None` so that downstream code never has to
guard against `q == ""`.

**Why a value object instead of a plain `str | None`?**
Wrapping the parameter makes it explicit at call sites that query state is being passed, and
the validator enforces the invariant in a single place rather than in every caller.
