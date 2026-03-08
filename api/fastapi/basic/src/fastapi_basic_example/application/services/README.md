# application/services

Application services encapsulate domain-level operations that don't belong to a single use
case. They are injected into route handlers via FastAPI's DI and may coordinate multiple
domain operations or cross-cutting concerns.

## Files

| File | Class | Responsibility |
|---|---|---|
| `health_service.py` | `HealthService` | Health and Kubernetes probe logic |

## HealthService

Answers the three standard Kubernetes health questions:

| Method | Route | Question |
|---|---|---|
| `get_health_status()` | `GET /health` | What is the current health status? |
| `is_alive() → bool` | `GET /health/live` | Is the process running? |
| `is_ready() → bool` | `GET /health/ready` | Is the process ready to accept traffic? |

`is_alive()` is also used by the startup probe (`GET /health/startup`).

All three methods currently return `True`/`"healthy"` unconditionally. To add real checks
(e.g. database ping, dependency connectivity), modify the method body. The probe route
handlers in `adapters/inbound/http/routers.py` handle the `False` case by raising HTTP 503.

## Service vs use case

- A **service** is used when an operation spans multiple domain concerns or is reused
  across several routes (health checks are called by three probe endpoints).
- A **use case** is preferred when the operation represents a single distinct user intent
  with clear input and output (e.g. "get item by ID").

See `../README.md` for the full application layer overview.
