# FastAPI OAuth Example

A complete FastAPI application demonstrating OAuth2 JWT authentication with PostgreSQL, built using hexagonal architecture.

## Features

- **User Registration**: Create new user accounts with email and password
- **JWT Authentication**: Secure token-based authentication using OAuth2 password flow
- **Password Hashing**: Bcrypt password hashing for security
- **Token Verification**: Validate and decode JWT tokens
- **PostgreSQL Integration**: Async database operations with SQLAlchemy
- **Hexagonal Architecture**: Clean separation of concerns (Domain, Application, Infrastructure)
- **Docker Support**: Complete Docker Compose setup with PostgreSQL

## Architecture

This project follows hexagonal (ports and adapters) architecture:

```
src/fastapi_oauth_example/
├── domain/              # Business logic and entities
│   ├── entities/        # User entity
│   ├── repositories/    # Repository interfaces
│   └── value_objects/   # Email, UserId value objects
├── application/         # Use cases and DTOs
│   ├── dto/             # Data Transfer Objects
│   └── use_cases/       # Register, Login, Verify Token
└── infrastructure/      # External concerns
    ├── config/          # Settings and configuration
    ├── di/              # Dependency injection
    ├── persistence/     # PostgreSQL implementation
    ├── security/        # JWT and password hashing
    └── web/             # FastAPI routes
```

## Requirements

- Python 3.13+
- PostgreSQL 16+ (via Docker)
- uv (Python package manager)

## Quick Start

### 1. Clone and Navigate

```bash
cd /path/to/python-lab/api/fastapi/oauth
```

### 2. Install Dependencies

```bash
uv sync
```

### 3. Start Services with Docker Compose

```bash
docker-compose up --build
```

This will start:
- FastAPI application on http://localhost:8000
- PostgreSQL database on port 5432

### 4. Access API Documentation

Open your browser to:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Endpoints

### Authentication

#### Register User
```http
POST /auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "username": "johndoe",
  "password": "securepassword123"
}
```

#### Login (Get Token)
```http
POST /auth/token
Content-Type: application/x-www-form-urlencoded

username=johndoe&password=securepassword123
```

Response:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
```

#### Get Current User
```http
GET /auth/me
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

Response:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "username": "johndoe",
  "is_active": true,
  "is_verified": false,
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-01T00:00:00"
}
```

### Health Check
```http
GET /health
```

## Configuration

Environment variables can be set in `.env` file or through Docker Compose:

```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@postgres:5432/fastapi_oauth
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## Development

### Run Locally (without Docker)

1. Start PostgreSQL:
```bash
docker run -d \
  --name postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=fastapi_oauth \
  -p 5432:5432 \
  postgres:16-alpine
```

2. Run the application:
```bash
uv run python -m fastapi_oauth_example.main
```

### Run Tests

```bash
uv run pytest
```

### Code Quality

```bash
# Format code
uv run ruff format .

# Lint code
uv run ruff check .
```

## Key Technologies

- **FastAPI**: Modern, fast web framework for building APIs
- **SQLAlchemy**: SQL toolkit and ORM with async support
- **PostgreSQL**: Powerful, open source relational database
- **python-jose**: JOSE implementation for JWT tokens
- **passlib**: Password hashing library with bcrypt support
- **Pydantic**: Data validation using Python type annotations
- **uvicorn**: Lightning-fast ASGI server

## Security Features

1. **Password Hashing**: Passwords are hashed using bcrypt before storage
2. **JWT Tokens**: Stateless authentication with signed tokens
3. **Token Expiration**: Configurable token lifetime (default 30 minutes)
4. **Email Validation**: Email addresses validated with proper regex
5. **Unique Constraints**: Email and username uniqueness enforced at database level

## OAuth2 Flow

This application implements the OAuth2 Password Flow:

1. User submits username and password to `/auth/token`
2. Server validates credentials and returns JWT access token
3. Client includes token in Authorization header for protected endpoints
4. Server validates token and extracts user information

## Testing in Swagger UI

1. Navigate to http://localhost:8000/docs
2. Click **POST /auth/register** to create a user
3. Click **POST /auth/token** or the "Authorize" button 🔒
4. Enter username and password
5. Click "Authorize" - token is automatically added to all requests
6. Test **GET /auth/me** to see your user information

## Database Schema

### Users Table

| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | Primary Key |
| email | String(255) | Unique, Indexed |
| username | String(100) | Unique, Indexed |
| hashed_password | String(255) | Not Null |
| is_active | Boolean | Default: True |
| is_verified | Boolean | Default: False |
| created_at | DateTime | Not Null |
| updated_at | DateTime | Not Null |

## License

MIT

## Contributing

Contributions are welcome! Please ensure:
- Code follows existing architecture patterns
- Tests are included for new features
- Code passes linting and formatting checks
