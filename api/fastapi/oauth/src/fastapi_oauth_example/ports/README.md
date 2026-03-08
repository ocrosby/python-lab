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
    └── user_repository.py   # driven port: user persistence contract
```

### Why is `inbound/` empty?

The use cases in `application/use_cases/` already *are* the inbound API surface. FastAPI
routes call them directly via dependency injection. Introducing a separate inbound port
interface would add indirection with no benefit at this scale. The directory is kept to
make the hexagonal intent explicit and to provide a clear location if inbound port
interfaces are needed in the future.

---

## outbound/user_repository.py

Defines the `UserRepository` abstract base class — the contract that any persistent storage
adapter must fulfil.

```python
class UserRepository(ABC):
    @abstractmethod
    async def get_by_id(self, user_id: UUID) -> User | None: ...

    @abstractmethod
    async def get_by_email(self, email: str) -> User | None: ...

    @abstractmethod
    async def save(self, user: User) -> User: ...

    @abstractmethod
    async def delete(self, user_id: UUID) -> bool: ...
```

### Dependency direction

```
application/use_cases/  ──depends on──►  ports/outbound/user_repository.py
                                                 ▲
                                                 │ implements
                         adapters/outbound/persistence/postgres_user_repository.py
```

The application core has no knowledge of `PostgresUserRepository`. The DI container
(`infrastructure/di/dependencies.py`) is the only place that wires the port to an adapter.

---

## Adding a new outbound port

1. Create `ports/outbound/<name>.py` with an `ABC` subclass.
2. Implement it in `adapters/outbound/<category>/<name_impl>.py`.
3. Add a factory function in `infrastructure/di/dependencies.py` that returns the
   **abstract** type, not the concrete class.
4. Inject via `Annotated[MyPort, Depends(get_my_port)]` at the use-case layer.
