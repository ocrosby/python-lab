# ports/outbound

Outbound port interfaces define what the application core *needs* from the outside world.
Concrete implementations live in `adapters/outbound/` and are wired in
`infrastructure/di/dependencies.py`.

The application core depends on these abstractions; it never imports from `adapters/`.

## Files

| File | Class | Description |
|---|---|---|
| `item_repository.py` | `ItemRepository` | Contract for item persistence |

## ItemRepository

```python
class ItemRepository(ABC):
    @abstractmethod
    async def get_by_id(self, item_id: int) -> Item | None: ...

    @abstractmethod
    async def save(self, item: Item) -> Item: ...

    @abstractmethod
    async def delete(self, item_id: int) -> bool: ...
```

| Method | Semantics |
|---|---|
| `get_by_id` | Returns `None` if not found; never raises for a missing item |
| `save` | Upsert: create or update; returns the persisted entity |
| `delete` | Returns `True` if deleted, `False` if the item did not exist |

## Adding a new outbound port

1. Create `ports/outbound/<name>_port.py` (or `<name>_repository.py` for persistence).
2. Define an `ABC` with `@abstractmethod` for each operation the application needs.
3. Import only from `domain/` — no infrastructure or adapter imports allowed here.
4. Implement the port in `adapters/outbound/<category>/`.
5. Register a factory in `infrastructure/di/dependencies.py` that returns the abstract type.

See `../README.md` for the full ports layer overview.
