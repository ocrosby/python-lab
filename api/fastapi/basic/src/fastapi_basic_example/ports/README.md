# ports

The **ports** package defines the contracts (interfaces) that separate the application core
from the outside world. Ports follow the Dependency Inversion Principle: the application
core depends on abstractions it owns, not on concrete infrastructure implementations.

In hexagonal architecture terminology:
- **Inbound ports** are the API that *drives* the application (how callers reach the core).
- **Outbound ports** are the API the application *drives* (what the core needs from outside).

---

## Package layout

```
ports/
├── inbound/           # driving ports (currently empty — see note below)
└── outbound/
    └── item_repository.py   # driven port: persistent storage contract
```

### Why is `inbound/` empty?

The use cases in `application/use_cases/` already *are* the inbound API surface. FastAPI
routes call them directly via dependency injection. Introducing a separate inbound port
interface would add indirection with no benefit at this scale. The directory is kept to
make the hexagonal intent explicit and to provide a clear location if inbound port interfaces
are needed in the future (e.g. a message-queue consumer that shares the same use-case
interface as the HTTP adapter).

---

## outbound/item_repository.py

Defines the `ItemRepository` abstract base class — the contract that any persistent storage
adapter must fulfil.

```python
class ItemRepository(ABC):
    @abstractmethod
    async def get_by_id(self, item_id: int) -> Item | None: ...

    @abstractmethod
    async def save(self, item: Item) -> Item: ...

    @abstractmethod
    async def delete(self, item_id: int) -> bool: ...
```

### Method contracts

| Method | Returns | Notes |
|---|---|---|
| `get_by_id(item_id)` | `Item \| None` | `None` signals "not found"; caller decides whether to raise |
| `save(item)` | `Item` | Returns the persisted entity (may carry generated fields) |
| `delete(item_id)` | `bool` | `True` = deleted, `False` = not found |

### Dependency direction

```
application/use_cases/  ──depends on──►  ports/outbound/item_repository.py
                                                 ▲
                                                 │ implements
                               adapters/outbound/persistence/in_memory_item_repository.py
```

The application core has no knowledge of `InMemoryItemRepository` or any other concrete
storage class. The DI container (`infrastructure/di/dependencies.py`) is the only place
that wires the port to an adapter.

---

## Adding a new outbound port

1. Create `ports/outbound/<name>.py` with an `ABC` subclass.
2. Implement it in `adapters/outbound/<category>/<name_impl>.py`.
3. Add a factory function in `infrastructure/di/dependencies.py` that returns the
   **abstract** type, not the concrete class.
4. Inject via `Annotated[MyPort, Depends(get_my_port)]` at the use-case layer.
