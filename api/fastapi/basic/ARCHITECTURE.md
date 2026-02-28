# Hexagonal Architecture (Ports and Adapters)

## Overview

This project implements **Hexagonal Architecture** (also known as **Ports and Adapters**), a pattern that isolates the core business logic from external concerns like frameworks, databases, and UI.

```
┌─────────────────────────────────────────────────────────────┐
│                     Infrastructure Layer                     │
│  (Adapters: Web, Persistence, Config, Logging, etc.)       │
│                                                              │
│  ┌────────────────────────────────────────────────────┐   │
│  │              Application Layer                      │   │
│  │  (Use Cases, Services, DTOs, Commands)            │   │
│  │                                                     │   │
│  │  ┌──────────────────────────────────────────┐    │   │
│  │  │         Domain Layer                      │    │   │
│  │  │  (Entities, Value Objects, Repositories, │    │   │
│  │  │   Business Rules, Domain Events)         │    │   │
│  │  └──────────────────────────────────────────┘    │   │
│  └────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## Directory Structure

```
src/fastapi_basic_example/
├── domain/                    # Core Business Logic (Inner Hexagon)
│   ├── entities/              # Business entities
│   │   └── item.py            # Item entity with business rules
│   ├── repositories/          # Repository interfaces (Ports)
│   │   └── item_repository.py # Abstract repository interface
│   ├── value_objects/         # Domain value objects
│   │   ├── health_status.py   # Health status value object
│   │   ├── item_id.py         # Type-safe item ID
│   │   └── query_params.py    # Query parameters value object
│   ├── events/                # Domain events (future)
│   ├── specifications/        # Specification pattern (future)
│   ├── utils/                 # Domain utilities
│   ├── constants.py           # Domain constants
│   ├── errors.py              # Domain-specific errors
│   └── result.py              # Result pattern for error handling
│
├── application/               # Application Use Cases (Middle Layer)
│   ├── use_cases/             # Application-specific business logic
│   │   └── get_item_use_case.py # Get item use case
│   ├── services/              # Application services
│   │   └── health_service.py  # Health check service
│   ├── dto/                   # Data Transfer Objects
│   │   └── item_dto.py        # Item DTOs for API responses
│   ├── commands/              # Command/Query pattern
│   │   └── base.py            # Base command interfaces
│   └── builders/              # Builder pattern (future)
│
└── infrastructure/            # External Adapters (Outer Layer)
    ├── web/                   # Web adapter (HTTP/REST)
    │   └── routers.py         # FastAPI routers
    ├── persistence/           # Persistence adapter (Database)
    │   └── in_memory_item_repository.py # In-memory implementation
    ├── di/                    # Dependency Injection
    │   └── dependencies.py    # FastAPI dependencies
    ├── config/                # Configuration adapter
    │   └── settings.py        # Application settings
    ├── logging/               # Logging adapter
    │   ├── config.py          # Logging configuration
    │   ├── context.py         # Logging context
    │   └── middleware.py      # Logging middleware
    ├── decorators/            # Infrastructure decorators
    │   └── logging.py         # Logging decorator
    └── utils/                 # Infrastructure utilities
        ├── datetime_utils.py  # DateTime utilities
        ├── id_generator.py    # ID generation
        └── time_provider.py   # Time provider abstraction
```

## Layer Descriptions

### 1. Domain Layer (Core)

**Purpose**: Contains business logic and rules, independent of any framework or external concern.

**Key Components**:

#### Entities (`domain/entities/`)
Business objects with identity and lifecycle.

```python
# domain/entities/item.py
class Item(BaseModel):
    """Item entity representing a business item."""
    item_id: int = Field(..., gt=0)
    name: str | None = None
    description: str | None = None
```

**Characteristics**:
- Immutable (frozen=True)
- Self-validating (Pydantic validators)
- Business rules encapsulated
- No framework dependencies

#### Value Objects (`domain/value_objects/`)
Immutable objects defined by their values, not identity.

```python
# domain/value_objects/item_id.py
@dataclass(frozen=True)
class ItemId:
    """Type-safe item ID value object."""
    value: int
    
    def __post_init__(self):
        if self.value <= 0:
            raise ValueError("ItemId must be positive")
```

**Benefits**:
- Type safety (no primitive obsession)
- Encapsulated validation
- Self-documenting code
- Immutable by design

#### Repository Interfaces (`domain/repositories/`)
**Ports** that define how to access entities.

```python
# domain/repositories/item_repository.py
class ItemRepository(ABC):
    """Abstract repository for Item entities (PORT)."""
    
    @abstractmethod
    async def get_by_id(self, item_id: int) -> Item | None:
        """Get item by ID."""
        pass
```

**Key Points**:
- Abstract interfaces only (no implementation)
- Define the contract for data access
- Domain layer doesn't know about databases
- Dependency inversion principle

#### Result Pattern (`domain/result.py`)
Explicit error handling without exceptions.

```python
from domain.result import Success, Failure, Result

async def get_item(item_id: int) -> Result[Item, ItemNotFoundError]:
    item = await repository.get_by_id(item_id)
    if item is None:
        return Failure(ItemNotFoundError(item_id))
    return Success(item)
```

### 2. Application Layer (Use Cases)

**Purpose**: Orchestrates domain logic and coordinates workflows. Contains application-specific business rules.

#### Use Cases (`application/use_cases/`)
Implement specific application behaviors.

```python
# application/use_cases/get_item_use_case.py
class GetItemUseCase:
    """Use case for getting an item."""
    
    def __init__(self, item_repository: ItemRepository):
        self._item_repository = item_repository
    
    async def execute(
        self, item_id: int, query_params: QueryParams | None = None
    ) -> ItemResponseDTO:
        """Execute the get item use case."""
        q_value = query_params.q if query_params else None
        return ItemResponseDTO(item_id=item_id, q=q_value)
```

**Characteristics**:
- Orchestrates domain objects
- Depends on repository interfaces (not implementations)
- Returns DTOs (not domain entities)
- Framework-independent

#### Services (`application/services/`)
Application services that coordinate multiple use cases or provide cross-cutting functionality.

```python
# application/services/health_service.py
class HealthService:
    """Service for health checks."""
    
    async def is_alive(self) -> bool:
        """Check if service is alive."""
        return True
    
    async def is_ready(self) -> bool:
        """Check if service is ready."""
        return True
```

#### DTOs (`application/dto/`)
Data Transfer Objects for moving data between layers.

```python
# application/dto/item_dto.py
class ItemResponseDTO(BaseModel):
    """DTO for item responses."""
    item_id: int = Field(..., gt=0)
    q: str | None = None
```

**Purpose**:
- Decouple internal domain from external representation
- API versioning without changing domain
- Validation at the boundary

### 3. Infrastructure Layer (Adapters)

**Purpose**: Implements external concerns and adapts them to the application's needs.

#### Web Adapter (`infrastructure/web/`)
Handles HTTP requests and responses (FastAPI).

```python
# infrastructure/web/routers.py
@router.get("/items/{item_id}", response_model=ItemResponseDTO)
async def read_item(
    item_id: int,
    use_case: Annotated[GetItemUseCase, Depends(get_item_use_case)],
) -> ItemResponseDTO:
    """Get item by ID."""
    return await use_case.execute(item_id)
```

**Responsibilities**:
- Route HTTP requests
- Handle request/response serialization
- Translate HTTP errors
- Inject dependencies

#### Persistence Adapter (`infrastructure/persistence/`)
**Adapters** that implement repository interfaces.

```python
# infrastructure/persistence/in_memory_item_repository.py
class InMemoryItemRepository(ItemRepository):
    """In-memory implementation of ItemRepository (ADAPTER)."""
    
    def __init__(self):
        self._items: dict[int, Item] = {}
    
    async def get_by_id(self, item_id: int) -> Item | None:
        """Get item by ID from memory."""
        return self._items.get(item_id)
```

**Key Points**:
- Implements repository interface (Port)
- Contains database-specific logic
- Can be swapped without changing domain
- Examples: PostgreSQL, MongoDB, Redis, etc.

#### Dependency Injection (`infrastructure/di/`)
Wires everything together using FastAPI's DI system.

```python
# infrastructure/di/dependencies.py
def get_item_repository() -> ItemRepository:
    """Dependency for item repository."""
    return InMemoryItemRepository()

def get_item_use_case(
    repository: Annotated[ItemRepository, Depends(get_item_repository)],
) -> GetItemUseCase:
    """Dependency for get item use case."""
    return GetItemUseCase(repository)
```

**Benefits**:
- Loose coupling
- Easy testing (mock dependencies)
- Configuration in one place

#### Configuration (`infrastructure/config/`)
Application configuration and settings.

```python
# infrastructure/config/settings.py
class Settings(BaseSettings):
    """Application settings."""
    app_name: str = "FastAPI Basic Example"
    debug: bool = False
```

## Dependency Flow

```
┌─────────────┐
│   Router    │ (Infrastructure - Web Adapter)
│  (HTTP In)  │
└──────┬──────┘
       │ Depends on
       ↓
┌─────────────┐
│  Use Case   │ (Application Layer)
│             │
└──────┬──────┘
       │ Depends on (Interface)
       ↓
┌─────────────┐
│ Repository  │ (Domain - Port/Interface)
│ (Interface) │
└─────────────┘
       ↑
       │ Implements
┌──────┴──────┐
│  Concrete   │ (Infrastructure - Adapter)
│ Repository  │
└─────────────┘
```

**Key Principle**: Dependencies point **inward**
- Infrastructure depends on Application
- Application depends on Domain
- Domain depends on nothing

## Request Flow Example

Let's trace a request through the architecture:

```
1. HTTP Request
   GET /items/123?q=test
   ↓
   
2. Web Adapter (infrastructure/web/routers.py)
   @router.get("/items/{item_id}")
   async def read_item(item_id: int, q: str | None, use_case: GetItemUseCase)
   ↓
   
3. Dependency Injection (infrastructure/di/dependencies.py)
   - Creates InMemoryItemRepository (adapter)
   - Creates GetItemUseCase with repository
   ↓
   
4. Use Case (application/use_cases/get_item_use_case.py)
   async def execute(item_id: int, query_params: QueryParams | None)
   - Validates input (via QueryParams value object)
   - Calls repository interface
   ↓
   
5. Repository (domain/repositories/item_repository.py)
   async def get_by_id(item_id: int) -> Item | None
   - Actual implementation in InMemoryItemRepository
   ↓
   
6. Domain Entity (domain/entities/item.py)
   class Item(BaseModel)
   - Returns validated entity
   ↓
   
7. DTO Conversion (application/dto/item_dto.py)
   ItemResponseDTO(item_id=..., q=...)
   - Converts entity to DTO
   ↓
   
8. HTTP Response (automatically by FastAPI)
   {"item_id": 123, "q": "test"}
```

## Benefits of This Architecture

### 1. **Testability**
```python
# Easy to test use case with mock repository
async def test_get_item():
    mock_repo = MockItemRepository()
    use_case = GetItemUseCase(mock_repo)
    result = await use_case.execute(123)
    assert result.item_id == 123
```

### 2. **Flexibility**
Replace implementations without changing core logic:
```python
# Switch from in-memory to PostgreSQL
def get_item_repository() -> ItemRepository:
    return PostgreSQLItemRepository()  # Just change the adapter
```

### 3. **Framework Independence**
Domain and application layers don't depend on FastAPI:
```python
# Could easily switch to Flask, Django, etc.
# Only infrastructure/web/ would change
```

### 4. **Clear Boundaries**
Each layer has a specific responsibility:
- **Domain**: Business rules
- **Application**: Use cases
- **Infrastructure**: Technical concerns

### 5. **Maintainability**
Changes are localized:
- Database change? → Only persistence adapter
- API change? → Only web adapter
- Business rule change? → Only domain layer

## Key Patterns Used

### 1. **Repository Pattern** (Port)
- Interface: `domain/repositories/item_repository.py`
- Implementation: `infrastructure/persistence/in_memory_item_repository.py`

### 2. **Dependency Injection**
- Configuration: `infrastructure/di/dependencies.py`
- Usage: FastAPI's `Depends()`

### 3. **Value Objects**
- Examples: `ItemId`, `QueryParams`, `HealthStatus`
- Location: `domain/value_objects/`

### 4. **Result Pattern**
- Implementation: `domain/result.py`
- Usage: Explicit error handling

### 5. **DTO Pattern**
- Location: `application/dto/`
- Purpose: Decouple internal from external representation

### 6. **Use Case Pattern**
- Location: `application/use_cases/`
- Purpose: Single responsibility per business operation

## Testing Strategy

### Unit Tests (Domain)
```python
# Test domain entities and value objects
def test_item_validation():
    with pytest.raises(ValueError):
        Item(item_id=-1)  # Should fail validation
```

### Use Case Tests (Application)
```python
# Test use cases with mock repositories
async def test_get_item_use_case():
    mock_repo = MockItemRepository()
    use_case = GetItemUseCase(mock_repo)
    result = await use_case.execute(123)
    assert result.item_id == 123
```

### Integration Tests (Infrastructure)
```python
# Test full request flow
async def test_get_item_endpoint(client: TestClient):
    response = client.get("/items/123")
    assert response.status_code == 200
```

## Evolution Path

As the application grows:

1. **Add new adapters**: PostgreSQL, Redis, RabbitMQ
2. **Enhance domain**: Specifications, domain events
3. **Expand use cases**: Complex workflows
4. **Add patterns**: CQRS, Event Sourcing

The architecture supports this growth without major refactoring.

## References

- **Hexagonal Architecture**: Alistair Cockburn
- **Clean Architecture**: Robert C. Martin
- **Domain-Driven Design**: Eric Evans
- **Ports and Adapters**: [https://alistair.cockburn.us/hexagonal-architecture/](https://alistair.cockburn.us/hexagonal-architecture/)

## See Also

- [DESIGN_PATTERNS.md](DESIGN_PATTERNS.md) - Design patterns used in this project
- [README.md](README.md) - Project overview and setup
