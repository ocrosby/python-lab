# application/services

Application services encapsulate business logic that does not belong to a single use case
or entity. Services have no dependency on the HTTP layer; routers call them through DI.

## Files

| File | Class(es) | Description |
|---|---|---|
| `health_service.py` | `HealthService` | Liveness / readiness / startup probe logic |
| `email_service.py` | `EmailService`, `ConsoleEmailService` | Email delivery abstraction |

## HealthService

Answers the three standard Kubernetes health probe questions.

| Method | Used by | Meaning |
|---|---|---|
| `get_health_status()` | `GET /health` | Returns current status + uptime |
| `is_alive()` | `GET /health/live` | Is the process running? |
| `is_ready()` | `GET /health/ready` | Is the process ready to accept traffic? |

## EmailService

Abstract base class for email delivery. `ConsoleEmailService` is the development
implementation that prints emails to stdout instead of sending them. Replace with an
SMTP or third-party implementation by subclassing `EmailService` and registering it
in `infrastructure/di/dependencies.py`.
