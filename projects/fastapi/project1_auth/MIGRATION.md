# Domain-Driven Design Migration

This document describes the new domain-driven package structure for the FastAPI project.

## New Structure

```
project1_auth/
├── src/                          # Source code (new domain-driven structure)
│   ├── core/                     # Core application functionality
│   │   ├── config.py            # Settings/configuration
│   │   ├── constants.py         # Application constants
│   │   ├── dependencies.py      # FastAPI dependencies
│   │   ├── middleware.py        # Custom middleware
│   │   ├── exceptions.py        # Custom exception handlers
│   │   └── security.py          # Security utilities
│   │
│   ├── domain/                   # Domain models (business logic)
│   │   ├── auth/
│   │   │   ├── models.py        # User, Token domain models
│   │   │   ├── service.py       # AuthService
│   │   │   ├── repository.py    # UserRepository, TokenRepository
│   │   │   └── exceptions.py    # Auth-specific exceptions
│   │   │
│   │   └── items/
│   │       ├── models.py
│   │       ├── service.py
│   │       ├── repository.py
│   │       └── exceptions.py
│   │
│   ├── api/                      # API layer (presentation)
│   │   ├── v1/
│   │   │   ├── auth.py          # Auth endpoints
│   │   │   ├── items.py         # Item endpoints
│   │   │   └── health.py        # Health endpoints
│   │   │
│   │   └── schemas/              # DTOs/Request/Response models
│   │       ├── auth.py
│   │       ├── items.py
│   │       └── common.py
│   │
│   └── infrastructure/            # External concerns
│       ├── database.py           # Database connection
│       └── rate_limiting.py      # Rate limiter
│
├── tests/
│   ├── unit/
│   │   └── domain/
│   │       ├── test_auth_service.py
│   │       └── test_item_service.py
│   │
│   └── integration/
│       └── test_api.py
│
├── scripts/
│   └── tasks.py                  # Invoke tasks
│
├── docker/
│   ├── Dockerfile
│   └── compose.yaml
│
└── main.py                        # Application entry point (root)
```

## Migration Status

### ✅ Completed
- Created new directory structure under `src/`
- Organized files by domain (auth, items)
- Separated API layer from domain layer
- Split DTOs into domain-specific schemas
- Organized tests into unit and integration
- Moved Docker files to `docker/` directory
- Moved build tasks to `scripts/` directory

### ⏳ Pending
- Update all import statements to use new paths
- Update `pyproject.toml` to configure Python path for `src/`
- Update `Dockerfile` to work with new structure
- Update `tasks.py` to reference new paths
- Run full test suite to verify migration

## Benefits of New Structure

1. **Separation of Concerns**: Clear boundaries between domain, API, and infrastructure
2. **Scalability**: Easy to add new domains (e.g., orders, payments)
3. **Testability**: Domain logic is isolated and easily testable
4. **Maintainability**: Related code is grouped together
5. **API Versioning**: Built-in support for v1, v2, etc.
6. **Domain-Driven Design**: Follows DDD principles with clear domain boundaries

## Next Steps

To complete the migration:

1. Update `pyproject.toml` to add `src` to Python path
2. Update all imports in `src/` files to use absolute imports from `src`
3. Update `main.py` to import from `src` package
4. Update `Dockerfile` PYTHONPATH or working directory
5. Update `docker/compose.yaml` paths if needed
6. Run tests: `inv test`
7. Fix any import errors
8. Clean up old files in root directory

## Import Examples

### Old Import Style (Root Level)
```python
from models import User, UserCreate
from repository import UserRepository
from auth_service import AuthService
```

### New Import Style (Domain-Driven)
```python
from src.domain.auth.models import User, UserCreate
from src.domain.auth.repository import UserRepository
from src.domain.auth.service import AuthService
```

Or with relative imports within the same domain:
```python
from .models import User, UserCreate
from .repository import UserRepository
```

## Running the Application

Once migration is complete:

```bash
# Development
inv dev

# Production
inv up

# Tests
inv test
```
