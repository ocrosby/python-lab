# FastAPI Project

A production-ready FastAPI application.

## Requirements

- Docker and Docker Compose
- Python 3.12+
- [uv](https://docs.astral.sh/uv/) for dependency management

## Setup

Install all dependencies (including development tools):

```bash
uv sync --all-groups
```

## Build Tasks

This project uses [Invoke](https://www.pyinvoke.org/) to manage build tasks. Available tasks:

### Development

```bash
inv dev
```

Runs the development server with hot reload at `http://localhost:8000`

### Docker Build

```bash
inv build
```

Builds the Docker image tagged as `project1:latest`

### Production Deployment

```bash
inv up
```

Starts the production server using Docker Compose at `http://localhost:8080`

```bash
inv down
```

Stops all running containers

### Testing

```bash
inv test
```

Builds the Docker image and runs the full test suite using Testcontainers

### Cleanup

```bash
inv clean
```

Removes all containers, volumes, and the Docker image

## API Documentation

When running, interactive API documentation is available:

- Swagger UI: `http://localhost:8080/docs` (production) or `http://localhost:8000/docs` (dev)
- ReDoc: `http://localhost:8080/redoc` (production) or `http://localhost:8000/redoc` (dev)

## Testing with Testcontainers

This project uses [Testcontainers](https://testcontainers.com/) to run integration tests against the Dockerized API.

### Prerequisites

1. Ensure Docker is running
2. Install dependencies: `uv sync --all-groups`

### Run Tests

Using Invoke (recommended):

```bash
inv test
```

Or directly with pytest:

```bash
docker build -t project1:latest .
uv run pytest tests/ -v
```

### What Gets Tested

The test suite validates:
- Root endpoint (`/`)
- Item retrieval endpoints (`/items/{item_id}`)
- Health check endpoints:
  - `/health/liveness` - Application is alive
  - `/health/readiness` - Application is ready to serve traffic
  - `/health/startup` - Application has completed startup

### How It Works

Testcontainers automatically:
1. Starts a Docker container with your application
2. Waits for the application to be ready
3. Runs the test suite against the containerized API
4. Tears down the container after tests complete

This ensures tests run against the same Docker image that will be deployed to production.

## Project Structure

```
.
├── main.py              # FastAPI application
├── tasks.py             # Invoke build tasks
├── tests/
│   └── test_api.py      # Integration tests with Testcontainers
├── Dockerfile           # Production Docker image
├── compose.yaml         # Docker Compose configuration
└── pyproject.toml       # Project dependencies
```
