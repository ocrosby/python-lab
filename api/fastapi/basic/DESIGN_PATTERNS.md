# Design Patterns Implementation Guide

This document describes the design patterns implemented in this application and how to use them.

## Implemented Patterns

### 1. Result Pattern (High Priority - Implemented)

**Location:** `src/fastapi_basic_example/domain/result.py`

**Purpose:** Explicit error handling without exceptions

**Usage:**
```python
from domain.result import Success, Failure, Result
from domain.errors import ItemNotFoundError

async def get_item(item_id: int) -> Result[Item, ItemNotFoundError]:
    item = await repository.get_by_id(item_id)
    if item is None:
        return Failure(ItemNotFoundError(item_id))
    return Success(item)

# In router:
result = await get_item(123)
if result.is_failure():
    raise HTTPException(status_code=404, detail=str(result.error))
return result.value
```

**Benefits:**
- No hidden exceptions
- Explicit error types
- Better testability
- Functional programming style

---

### 2. Command/Query Pattern (High Priority - Implemented)

**Location:** `src/fastapi_basic_example/application/commands/base.py`

**Purpose:** Consistent interface for business operations (CQRS)

**Usage:**
```python
from application.commands.base import Query
from domain.result import Result, Success
from domain.errors import ItemNotFoundError

class GetItemQuery(Query[int, ItemResponseDTO, ItemNotFoundError]):
    def __init__(self, repository: ItemRepository):
        self._repository = repository
    
    async def execute(self, item_id: int) -> Result[ItemResponseDTO, ItemNotFoundError]:
        item = await self._repository.get_by_id(item_id)
        if item is None:
            return Failure(ItemNotFoundError(item_id))
        return Success(ItemResponseDTO.from_entity(item))
```

**Benefits:**
- Consistent operation interface
- Easy to add middleware (logging, caching)
- CQRS-ready architecture
- Separation of reads and writes

---

### 3. Logging Decorator Pattern (High Priority - Recommended)

**Location:** `src/fastapi_basic_example/infrastructure/decorators/logging.py`

**Purpose:** DRY logging across use cases/services

**Usage:**
```python
from infrastructure.decorators.logging import log_execution

class GetItemUseCase:
    @log_execution("use_cases")
    async def execute(self, item_id: int) -> ItemResponseDTO:
        # Automatic logging of entry, exit, and errors
        return await self._get_item(item_id)
```

**Implementation:**
```python
import functools
import structlog
from infrastructure.logging.context import get_logger_context

def log_execution(logger_name: str):
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            logger = structlog.get_logger(logger_name)
            func_name = func.__name__
            
            logger.info(f"Executing {func_name}", **get_logger_context())
            try:
                result = await func(*args, **kwargs)
                logger.info(f"Completed {func_name}", **get_logger_context())
                return result
            except Exception as e:
                logger.error(
                    f"Failed {func_name}",
                    error=str(e),
                    error_type=type(e).__name__,
                    **get_logger_context()
                )
                raise
        return wrapper
    return decorator
```

---

### 4. Strategy Pattern for Health Checks (Medium Priority - Recommended)

**Location:** `src/fastapi_basic_example/domain/health/`

**Purpose:** Pluggable health check components

**Usage:**
```python
# Define protocol
class HealthCheck(Protocol):
    async def check(self) -> bool:
        pass

# Implement checks
class DatabaseHealthCheck(HealthCheck):
    def __init__(self, db_client):
        self._db = db_client
    
    async def check(self) -> bool:
        try:
            await self._db.execute("SELECT 1")
            return True
        except:
            return False

# Compose in service
class HealthService:
    def __init__(self, checks: list[HealthCheck]):
        self._checks = checks
    
    async def is_ready(self) -> bool:
        results = await asyncio.gather(*[c.check() for c in self._checks])
        return all(results)
```

**Benefits:**
- Easy to add new checks
- Each check independently testable
- Configurable composition
- Open/Closed Principle

---

### 5. Value Object Pattern (Medium Priority - Recommended)

**Location:** `src/fastapi_basic_example/domain/value_objects/`

**Purpose:** Type-safe domain concepts

**Usage:**
```python
from dataclasses import dataclass

@dataclass(frozen=True)
class ItemId:
    value: int
    
    def __post_init__(self):
        if self.value <= 0:
            raise ValueError("ItemId must be positive")
    
    def __int__(self) -> int:
        return self.value
    
    def __str__(self) -> str:
        return str(self.value)

# Usage
item_id = ItemId(123)
result = await repository.get_by_id(int(item_id))
```

**Benefits:**
- Type safety
- Encapsulated validation
- No primitive obsession
- Self-documenting code

---

### 6. Specification Pattern (Medium Priority - Future)

**Location:** `src/fastapi_basic_example/domain/specifications/`

**Purpose:** Reusable query logic

**Usage:**
```python
class Specification(ABC):
    @abstractmethod
    def is_satisfied_by(self, candidate) -> bool:
        pass
    
    def and_(self, other: 'Specification') -> 'Specification':
        return AndSpecification(self, other)

class ItemByIdSpec(Specification):
    def __init__(self, item_id: int):
        self._item_id = item_id
    
    def is_satisfied_by(self, item: Item) -> bool:
        return item.item_id == self._item_id

# Usage
spec = ItemByIdSpec(123).and_(ActiveItemSpec())
items = await repository.find(spec)
```

---

### 7. Builder Pattern (Low Priority - Future)

**Location:** `src/fastapi_basic_example/application/builders/`

**Purpose:** Fluent DTO construction

**Usage:**
```python
class HealthCheckDTOBuilder:
    def __init__(self):
        self._status = None
        self._timestamp = None
        self._metadata = {}
    
    def with_status(self, status: str) -> 'HealthCheckDTOBuilder':
        self._status = status
        return self
    
    def with_timestamp(self, timestamp: str) -> 'HealthCheckDTOBuilder':
        self._timestamp = timestamp
        return self
    
    def build(self) -> HealthCheckDTO:
        return HealthCheckDTO(
            status=self._status,
            timestamp=self._timestamp,
            metadata=self._metadata
        )

# Usage
dto = (HealthCheckDTOBuilder()
    .with_status("healthy")
    .with_timestamp(current_utc_timestamp())
    .build())
```

---

### 8. Observer Pattern (Low Priority - Future)

**Location:** `src/fastapi_basic_example/domain/events/`

**Purpose:** Domain events for decoupling

**Usage:**
```python
@dataclass
class DomainEvent:
    occurred_at: datetime
    event_id: str

@dataclass
class ItemCreatedEvent(DomainEvent):
    item_id: int
    name: str

class Item:
    def __init__(self):
        self._events: list[DomainEvent] = []
    
    def create(self, item_id: int, name: str):
        # Business logic
        self._events.append(ItemCreatedEvent(
            occurred_at=datetime.now(),
            event_id=str(uuid.uuid4()),
            item_id=item_id,
            name=name
        ))
    
    def collect_events(self) -> list[DomainEvent]:
        events = self._events.copy()
        self._events.clear()
        return events
```

---

## Implementation Priority

### Phase 1: High Priority (Immediate)
1. ✅ Result Pattern - Already implemented
2. ✅ Command Pattern - Already implemented  
3. 🔧 Logging Decorator - Implement next
4. 🔧 Refactor existing use cases to use patterns

### Phase 2: Medium Priority (Next Sprint)
5. Strategy Pattern for Health Checks
6. Value Objects for domain concepts
7. Specification Pattern for queries

### Phase 3: Low Priority (Future Enhancement)
8. Builder Pattern for complex DTOs
9. Observer Pattern for domain events
10. Event Sourcing infrastructure

---

## Migration Strategy

### Step 1: Add New Patterns (Non-Breaking)
- Add Result, Command, Error classes
- Add decorator utilities
- Add value objects
- Keep existing code working

### Step 2: Refactor Use Cases (Gradual)
- Convert one use case at a time to use new patterns
- Update tests for each use case
- Ensure backward compatibility

### Step 3: Update Routers (Last)
- Update routers to handle Result pattern
- Convert HTTPExceptions to error responses
- Update API documentation

---

## Testing Strategy

### Unit Tests
```python
async def test_get_item_success():
    repository = MockRepository()
    use_case = GetItemQuery(repository)
    
    result = await use_case.execute(123)
    
    assert result.is_success()
    assert result.value.item_id == 123

async def test_get_item_not_found():
    repository = MockRepository()
    use_case = GetItemQuery(repository)
    
    result = await use_case.execute(999)
    
    assert result.is_failure()
    assert isinstance(result.error, ItemNotFoundError)
```

### Integration Tests
```python
async def test_get_item_api_success(client):
    response = client.get("/items/123")
    assert response.status_code == 200

async def test_get_item_api_not_found(client):
    response = client.get("/items/999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]
```

---

## References

- **Clean Architecture**: Robert C. Martin
- **Domain-Driven Design**: Eric Evans  
- **Patterns of Enterprise Application Architecture**: Martin Fowler
- **Python Design Patterns**: https://refactoring.guru/design-patterns/python

---

## Next Steps

1. Review this guide with the team
2. Implement logging decorator pattern
3. Refactor one use case as example
4. Create migration plan for remaining code
5. Update documentation and ADRs
