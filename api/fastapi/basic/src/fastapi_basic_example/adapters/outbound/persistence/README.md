# adapters/outbound/persistence

Persistence adapters implement storage-related ports. Currently contains a single
in-memory implementation suitable for development and testing.

## Files

| File | Class | Port implemented |
|---|---|---|
| `in_memory_item_repository.py` | `InMemoryItemRepository` | `ItemRepository` |

## InMemoryItemRepository

Stores `Item` entities in a plain Python `dict[int, Item]`. Each instance has its own
isolated store; no data is shared between instances.

```python
repo = InMemoryItemRepository()
await repo.save(Item(item_id=1))
item = await repo.get_by_id(1)    # → Item(item_id=1)
deleted = await repo.delete(1)    # → True
missing = await repo.get_by_id(1) # → None
```

## Replacing with a real database

1. Create `sql_item_repository.py` (or `mongo_item_repository.py`, etc.) in this directory.
2. Implement all three abstract methods from `ports/outbound/item_repository.py`.
3. In `infrastructure/di/dependencies.py`, update `get_item_repository()` to return an
   instance of the new class.

Because `get_item_repository()` is typed to return `ItemRepository` (the abstract port),
no call sites outside `dependencies.py` need to change.

See `../../README.md` for the full adapters layer overview.
