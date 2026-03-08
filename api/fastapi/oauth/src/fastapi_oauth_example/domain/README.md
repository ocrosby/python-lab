# domain

The **domain** package is the innermost layer of the hexagonal architecture. It contains
pure business concepts with no dependencies on any framework, database, HTTP library, or
other infrastructure concern. Everything here can be understood, instantiated, and tested
without importing FastAPI, SQLAlchemy, or any other external package.

---

## Package layout

```
domain/
├── entities/
│   └── user.py           # User entity (dataclass)
└── value_objects/
    ├── email.py          # Email value object with validation
    └── user_id.py        # UserId value object
```

---

## entities/user.py

`User` is the central domain entity. It encapsulates the identity and state of an
authenticated user, including MFA settings and account lockout tracking.

Entities are identified by their `user_id`. They are plain dataclasses — no Pydantic,
no ORM annotations.

---

## value_objects/

Value objects represent domain concepts that are equal by value, not by identity.

| Class | File | Description |
|---|---|---|
| `Email` | `email.py` | Validates and normalises an email address |
| `UserId` | `user_id.py` | Typed wrapper around a UUID user identifier |

---

## Rules

- No imports from `application/`, `adapters/`, `infrastructure/`, or `ports/`.
- No framework dependencies (FastAPI, SQLAlchemy, Pydantic, etc.).
- Domain errors raise standard Python `Exception` subclasses.
