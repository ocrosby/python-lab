# FastAPI Project

A production-ready FastAPI application with JWT authentication, refresh tokens, and user management.

## Features

- **JWT Authentication**: Secure token-based authentication with access and refresh tokens
- **User Registration & Login**: Complete user management with email and username support
- **Token Rotation**: Automatic refresh token rotation with family-based revocation
- **Rate Limiting**: Configurable rate limits on authentication endpoints
- **Health Checks**: Liveness, readiness, and startup health endpoints
- **Docker Support**: Full containerization with Docker Compose
- **Test Coverage**: Integration tests using Testcontainers

## Requirements

- Docker and Docker Compose
- Python 3.12+
- [uv](https://docs.astral.sh/uv/) for dependency management

## Setup

Install all dependencies (including development tools):

```bash
uv sync --all-groups
```

### Environment Variables

Create a `.env` file based on `.env.example`:

```bash
# Database
DATABASE_URL=postgresql://project1:project1@localhost:5432/project1
POSTGRES_DB=project1
POSTGRES_USER=project1
POSTGRES_PASSWORD=project1

# JWT Authentication
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Database Pool
DB_POOL_MIN_CONN=1
DB_POOL_MAX_CONN=10

# Logging
LOG_LEVEL=INFO
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

## Authentication API

### Register a New User

```bash
POST /api/v1/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "username": "username",
  "password": "secure_password"
}
```

**Response:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "username",
  "is_active": true
}
```

**Rate Limit:** 5 requests per minute

### Login (Get Access Token)

```bash
POST /api/v1/auth/token
Content-Type: application/x-www-form-urlencoded

username=username&password=secure_password
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "AbCdEf123456...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

**Rate Limit:** 10 requests per minute

### Get Current User

```bash
GET /api/v1/auth/me
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "username",
  "is_active": true
}
```

### Refresh Access Token

```bash
POST /api/v1/auth/refresh
Content-Type: application/json

{
  "refresh_token": "AbCdEf123456..."
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "XyZ789NewToken...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

**Rate Limit:** 20 requests per minute

**Note:** The old refresh token is automatically revoked and a new one is issued (token rotation).

### Revoke Refresh Token

```bash
POST /api/v1/auth/revoke
Content-Type: application/json

{
  "refresh_token": "AbCdEf123456..."
}
```

**Response:** `204 No Content`

## Security Features

### Token Rotation
- Refresh tokens are automatically rotated on each use
- Old refresh tokens are immediately revoked after creating new ones
- Token families track rotation chains

### Token Theft Detection
- If a revoked refresh token is used, the entire token family is revoked
- Forces re-authentication if token theft is suspected

### Password Security
- Passwords are hashed using bcrypt
- Async password verification prevents blocking operations

### Rate Limiting
- Registration: 5 requests per minute
- Login: 10 requests per minute
- Refresh: 20 requests per minute

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
- **Authentication endpoints:**
  - User registration with validation
  - User login with token generation
  - Token refresh with rotation
  - Token revocation
  - Protected endpoint access
- **Authorization:**
  - JWT token validation
  - User authentication and authorization
- **Health check endpoints:**
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

### Current Structure (Root-based)
The application currently uses a flat structure with files in the root directory.

### Recommended Structure (Domain-Driven Design)
A new domain-driven structure has been created under `src/` for better organization:

```
project1_auth/
├── src/                          # New domain-driven structure
│   ├── core/                     # Core application functionality
│   │   ├── config.py            # Settings/configuration
│   │   ├── dependencies.py      # FastAPI dependencies
│   │   ├── middleware.py        # Custom middleware
│   │   └── exceptions.py        # Exception handlers
│   │
│   ├── domain/                   # Domain models (business logic)
│   │   ├── auth/                # Authentication domain
│   │   │   ├── models.py        # User, Token models
│   │   │   ├── service.py       # AuthService
│   │   │   ├── repository.py    # Data access
│   │   │   └── exceptions.py    # Domain exceptions
│   │   │
│   │   └── items/               # Items domain
│   │       ├── models.py
│   │       ├── service.py
│   │       ├── repository.py
│   │       └── exceptions.py
│   │
│   ├── api/                      # API layer (presentation)
│   │   ├── v1/                  # API version 1
│   │   │   ├── auth.py          # Auth endpoints
│   │   │   ├── items.py         # Item endpoints
│   │   │   └── health.py        # Health endpoints
│   │   │
│   │   └── schemas/              # Request/Response schemas
│   │       ├── auth.py
│   │       ├── items.py
│   │       └── common.py
│   │
│   └── infrastructure/            # External concerns
│       ├── database.py           # Database connection
│       └── rate_limiting.py      # Rate limiter
│
├── tests/
│   ├── unit/domain/             # Unit tests for domain logic
│   └── integration/             # Integration tests
│
├── scripts/                      # Utility scripts
│   └── tasks.py                 # Invoke build tasks
│
├── docker/                       # Docker configuration
│   ├── Dockerfile
│   └── compose.yaml
│
└── main.py                       # Application entry point
```

See `MIGRATION.md` for details on migrating to the new structure.

## Architecture

This application follows **SOLID principles** and uses **Dependency Injection** for maximum testability:

- **Domain-Driven Design**: Clear separation between domains (auth, items)
- **Service Layer**: Business logic isolated in service classes
- **Repository Pattern**: Data access abstracted through repository interfaces
- **API Layer**: Presentation logic separated from business logic
- **DTOs/Schemas**: Clear contracts for API requests/responses
- **Dependency Injection**: FastAPI's DI system provides services to routes
- **Middleware**: Custom middleware for CORS, security headers, and logging
- **Exception Handlers**: Centralized error handling for consistent API responses

### Benefits of Domain-Driven Structure

1. **Scalability**: Easy to add new domains (orders, payments, etc.)
2. **Maintainability**: Related code is grouped together
3. **Testability**: Domain logic is isolated and easily testable
4. **API Versioning**: Built-in support for v1, v2, etc.
5. **Clear Boundaries**: Separation between domain, API, and infrastructure layers
