# adapters/outbound

Outbound adapters implement the ports defined in `ports/outbound/`. They translate
application-level calls into external system interactions — storage, caches, message
queues, third-party APIs, etc.

## Sub-packages

| Package | Technology | Description |
|---|---|---|
| `persistence/` | PostgreSQL + SQLAlchemy | `PostgresUserRepository` and token repositories |

## Adding a new outbound adapter

1. Create a sub-package for the technology (e.g. `persistence/`, `cache/`, `messaging/`).
2. Implement the relevant port abstract class from `ports/outbound/`.
3. Register the new adapter in `infrastructure/di/dependencies.py` by updating the
   factory function to return the new concrete class.
4. No other files need to change — the application core is unaware of the swap.

See `../README.md` for the full adapters layer overview.
