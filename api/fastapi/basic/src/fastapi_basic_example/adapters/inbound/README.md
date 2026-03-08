# adapters/inbound

Inbound adapters translate external calls into the application core. They receive requests
from outside, convert them into domain/application types, invoke the appropriate use case
or service, and convert the result back into the external protocol format.

## Sub-packages

| Package | Protocol | Description |
|---|---|---|
| `http/` | HTTP/REST | FastAPI route handlers |

## Adding a new inbound adapter

Create a new sub-package for the protocol (e.g. `grpc/`, `cli/`, `queue/`) and implement
the translation layer there. Each adapter should:

1. Accept input in the external protocol's native format.
2. Convert it to domain types (entities, value objects) or call application DTOs.
3. Call a use case or service injected via the DI container.
4. Convert the result to the external protocol's response format.

See `../README.md` for the full adapters layer overview.
