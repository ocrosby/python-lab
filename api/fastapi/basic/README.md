# FastAPI Basic Example

A simple FastAPI application demonstrating modern Python tooling with uv, ruff, and invoke, implemented using Hexagonal Architecture (Ports and Adapters).

## Features

- **Hexagonal Architecture** - Clean separation of business logic, application services, and infrastructure
- **Dependency Injection** - Using `dependency-injector` for IoC container management
- **Structured Logging** - JSON logging with correlation IDs using `structlog`
- **Health Checks** - Kubernetes-ready liveness, readiness, and startup probes
- **Modern Tooling** - Fast package management with `uv`, linting/formatting with `ruff`
- **Task Automation** - Invoke tasks with single-character aliases for developer ergonomics
- **Comprehensive Testing** - Unit, integration, and e2e tests with pytest
- **Type Safety** - Full type hints with Pydantic models

## Technology Stack

- **FastAPI** - Modern, fast web framework
- **Pydantic** - Data validation using Python type annotations
- **dependency-injector** - Dependency injection container
- **structlog** - Structured logging
- **uvicorn** - ASGI server
- **pytest** - Testing framework
- **ruff** - Fast Python linter and formatter
- **uv** - Fast Python package installer and resolver

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

Use `invoke --list` or `uv run inv --list` to see all available tasks. All tasks support single-character aliases for faster workflow:

```bash
# Development
invoke dev              # Start development server (alias: d)
invoke run              # Run the application (alias: r)

# Code Quality
invoke format           # Format code with ruff (alias: f)
invoke format-check     # Check code formatting (alias: k)
invoke lint             # Run ruff linter (alias: l)
invoke check            # Run all checks: format + lint (alias: c)

# Testing
invoke test             # Run all tests with coverage (alias: t)
invoke test-unit        # Run only unit tests (alias: u)
invoke test-integration # Run only integration tests (alias: n)
invoke test-e2e         # Run only e2e tests (alias: e)
invoke coverage-report  # Generate coverage report (alias: v)

# Building
invoke build            # Build Python package (alias: b)
invoke build-docker     # Build Docker image (alias: o)
invoke build-all        # Build package + Docker (alias: a)

# Utilities
invoke install          # Install dependencies (alias: i)
invoke clean            # Clean up cache files (alias: x)
```

**Note:** Tasks with prerequisites automatically run quality checks:
- `test` runs `lint` (which runs `format` first)
- `build` runs `check` (format + lint)
- `build-docker` runs `check` (format + lint)

### Example Usage

```bash
# Using full names
uv run invoke test
uv run invoke build-docker

# Using aliases (faster)
uv run inv t
uv run inv o
```

### Alternative Setup (Traditional)

1. Install dependencies:
   ```bash
   pip install -e .
   ```

2. Run the application:
   ```bash
   uvicorn src.fastapi_basic_example.main:app --reload
   ```

3. Visit http://localhost:8000

### With Docker Compose

1. Build and run:
   ```bash
   docker-compose up --build
   ```

2. Visit http://localhost:8000

## Configuration

The application can be configured using environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `APP_NAME` | `fastapi-basic-example` | Application name |
| `APP_VERSION` | `1.0.0` | Application version |
| `LOG_LEVEL` | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL) |
| `JSON_LOGGING` | `false` | Enable JSON structured logging |

Example:
```bash
LOG_LEVEL=DEBUG JSON_LOGGING=true uv run invoke dev
```

## Dependency Injection

This project uses `dependency-injector` for managing dependencies. The DI container is defined in `src/fastapi_basic_example/infrastructure/di/container.py` and provides:

- Singleton services (HealthService)
- Repository implementations (InMemoryItemRepository)
- Use cases (GetItemUseCase)

Dependencies are injected into FastAPI routes using the `@inject` decorator and `Depends(Provide[Container.service_name])`.

## Testing

The project includes comprehensive tests organized by type:

### Running Tests

```bash
# Run all tests with coverage
uv run inv t

# Run only unit tests
uv run inv u

# Run only integration tests
uv run inv n

# Run only e2e tests
uv run inv e

# Generate coverage report
uv run inv v
```

### Test Organization

- **Unit Tests** (`tests/unit/`): Test individual components in isolation with mocks
- **Integration Tests** (`tests/integration/`): Test component interactions with DI container
- **E2E Tests** (`tests/e2e/`): Test complete API workflows with TestClient

All tests use pytest markers (`@pytest.mark.unit`, `@pytest.mark.integration`, `@pytest.mark.e2e`) for selective execution.

## API Endpoints

### Application Endpoints
- `GET /` - Welcome message with application info
- `GET /items/{item_id}` - Get item by ID with optional query parameter

### Health Check Endpoints
- `GET /health` - Basic health status
- `GET /health/detailed` - Detailed health status with uptime and metadata

### Kubernetes Probe Endpoints
- `GET /health/live` or `/healthz` - Liveness probe (is the app running?)
- `GET /health/ready` or `/readiness` - Readiness probe (is the app ready to serve traffic?)
- `GET /health/startup` - Startup probe (has the app finished starting?)

## Interactive Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Development Workflow

1. Make code changes
2. Run `uv run inv c` to check code quality (format + lint)
3. Run `uv run inv t` to run tests (automatically runs lint first)
4. Commit changes
5. Build with `uv run inv b` or `uv run inv o` (automatically runs checks first)

The task prerequisites ensure code quality is maintained throughout the development process.