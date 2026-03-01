# FastAPI Examples & Documentation

This directory contains FastAPI examples and comprehensive quick-reference documentation.

## 📚 Documentation

Comprehensive quick-reference guides for FastAPI features:

- **[Quick Reference Index](docs/README.md)** - Complete navigation to all FastAPI topics
- **[Quick Start Guide](docs/QUICKSTART.md)** - Get started in 5 minutes
- **[Documentation Status](docs/STATUS.md)** - Track documentation progress

Topics covered: Getting Started, Validation, Dependencies, Security, Testing, Deployment, and more.

## 🚀 Example Projects

### Basic Example
**[basic/](basic/)** - Production-ready FastAPI application demonstrating:
- Hexagonal Architecture (Ports and Adapters)
- Health checks and Kubernetes probes
- Structured logging with correlation IDs
- Comprehensive testing (98% coverage)
- Modern Python tooling (uv, ruff, invoke)

**Quick Links:**
- [Basic README](basic/README.md) - Setup and features
- [Architecture Guide](basic/ARCHITECTURE.md) - Hexagonal architecture explained
- [Design Patterns](basic/DESIGN_PATTERNS.md) - Patterns used in the project

### OAuth Example
**[oauth/](oauth/)** - Complete OAuth2 JWT authentication with:
- User registration and login
- JWT token-based authentication
- PostgreSQL database integration
- Password hashing with bcrypt
- Docker Compose setup

**Quick Links:**
- [OAuth README](oauth/README.md) - Setup and API endpoints

## 🏗️ Directory Structure

```
fastapi/
├── README.md              # This file
├── docs/                  # FastAPI quick reference documentation
│   ├── README.md          # Documentation index
│   ├── QUICKSTART.md      # Quick start guide
│   └── fastapi/           # Topic-organized guides
│       ├── 02-getting-started/
│       ├── 03-validation/
│       ├── 06-dependencies/
│       ├── 07-security/
│       └── ...
├── basic/                 # Basic example with hexagonal architecture
│   ├── README.md
│   ├── ARCHITECTURE.md
│   ├── src/
│   ├── tests/
│   └── ...
└── oauth/                 # OAuth2 JWT authentication example
    ├── README.md
    ├── src/
    ├── tests/
    └── ...
```

## 🎯 Quick Start

### New to FastAPI?
1. Read the **[Quick Start Guide](docs/QUICKSTART.md)**
2. Explore the **[Basic Example](basic/README.md)**
3. Check out the **[Getting Started Documentation](docs/fastapi/02-getting-started/first-steps.md)**

### Need Authentication?
Jump straight to the **[OAuth Example](oauth/README.md)** for a complete JWT authentication implementation.

### Looking for Specific Features?
Browse the **[Documentation Index](docs/README.md)** for quick-reference guides on:
- Path and query parameters
- Request validation
- Dependency injection
- Security and OAuth2
- Testing and deployment

## 💡 What is FastAPI?

FastAPI is a modern, fast web framework for building APIs with Python 3.7+ based on standard Python type hints.

### Key Features

- **Fast**: Very high performance, on par with NodeJS and Go
- **Fast to code**: Increase development speed by 200-300%
- **Fewer bugs**: Reduce human-induced errors by ~40%
- **Intuitive**: Great editor support with completion and type checking
- **Easy**: Designed to be easy to use and learn
- **Robust**: Production-ready with automatic interactive documentation
- **Standards-based**: Based on OpenAPI and JSON Schema

## 🔗 External Resources

- [FastAPI Official Documentation](https://fastapi.tiangolo.com/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Starlette Documentation](https://www.starlette.io/)