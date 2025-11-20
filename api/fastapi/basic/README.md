# FastAPI Basic Example

A simple FastAPI application demonstrating modern Python tooling with uv, ruff, and invoke, implemented using Hexagonal Architecture (Ports and Adapters).

## Architecture

This project implements **Hexagonal Architecture** (also known as Ports and Adapters), which provides clear separation of concerns and makes the application more testable and maintainable.

### Architecture Layers

- **Domain Layer** (`src/fastapi_basic_example/domain/`): Contains business logic, entities, and domain interfaces
  - `entities/`: Business objects (Item)
  - `repositories/`: Abstract repository interfaces
  - `value_objects/`: Domain value objects (QueryParams)

- **Application Layer** (`src/fastapi_basic_example/application/`): Orchestrates domain objects and implements use cases
  - `dto/`: Data Transfer Objects for external communication
  - `services/`: Application services (HealthService)
  - `use_cases/`: Business use cases (GetItemUseCase)

- **Infrastructure Layer** (`src/fastapi_basic_example/infrastructure/`): External concerns and adapters
  - `config/`: Configuration and settings
  - `persistence/`: Repository implementations (InMemoryItemRepository)
  - `web/`: HTTP adapters and routers

### Benefits of This Architecture

1. **Dependency Inversion**: Core business logic doesn't depend on external frameworks
2. **Testability**: Easy to unit test business logic in isolation
3. **Flexibility**: Can swap implementations (e.g., database, web framework) without affecting core logic
4. **Clear Boundaries**: Well-defined separation between business rules and technical concerns

## Project Structure

```
basic/
├── src/
│   └── fastapi_basic_example/
│       ├── domain/              # Business logic and rules
│       │   ├── entities/        # Business objects
│       │   ├── repositories/    # Repository interfaces
│       │   └── value_objects/   # Domain value objects
│       ├── application/         # Use cases and application services
│       │   ├── dto/             # Data transfer objects
│       │   ├── services/        # Application services
│       │   └── use_cases/       # Business use cases
│       ├── infrastructure/      # External adapters
│       │   ├── config/          # Configuration
│       │   ├── persistence/     # Repository implementations
│       │   └── web/             # HTTP/REST adapters
│       └── main.py              # Application entry point
├── tests/
│   ├── unit/                    # Unit tests
│   ├── integration/             # Integration tests
│   └── e2e/                     # End-to-end tests
├── main.py                      # FastAPI application
├── pyproject.toml               # Python project configuration
├── tasks.py                     # Invoke task definitions
├── Dockerfile                   # Container image definition
├── docker-compose.yml           # Multi-container orchestration
├── .dockerignore                # Docker build exclusions
└── README.md                   # This file
```

## Development Setup

### Prerequisites
- Python 3.13+

### Install uv (Package Manager)

#### macOS/Linux
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

#### Windows (PowerShell)
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

#### Alternative: Using pip
```bash
pip install uv
```

#### Verify Installation
```bash
uv --version
```

### Install ruff (Linter/Formatter) - Optional

ruff will be installed automatically with the project dependencies, but you can install it globally:

#### Using uv
```bash
uv tool install ruff
```

#### Using pip
```bash
pip install ruff
```

### Quick Start

1. Install dependencies:
   ```bash
   uv sync --dev
   ```

2. Run the application:
   ```bash
   invoke dev
   ```
   or
   ```bash
   uv run invoke dev
   ```

3. Visit http://localhost:8000

## Available Tasks

Use `invoke --list` to see all available tasks:

```bash
# Development
invoke dev              # Start development server
invoke run              # Run the application (production-like)

# Code Quality
invoke lint             # Run ruff linter
invoke format           # Format code with ruff
invoke format-check     # Check code formatting
invoke check            # Run all checks (format + lint)

# Testing
invoke test             # Run tests with pytest

# Utilities
invoke install          # Install dependencies
invoke clean            # Clean up cache files
invoke build            # Build the project
```

### Alternative Setup (Traditional)

1. Install dependencies:
   ```bash
   pip install -e .
   ```

2. Run the application:
   ```bash
   uvicorn main:app --reload
   ```

3. Visit http://localhost:8000

### With Docker Compose

1. Build and run:
   ```bash
   docker-compose up --build
   ```

2. Visit http://localhost:8000

## API Endpoints

- `GET /` - Hello World message
- `GET /items/{item_id}` - Get item by ID with optional query parameter
- `GET /health` - Health check endpoint

## Interactive Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc