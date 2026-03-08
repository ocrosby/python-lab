# adapters/inbound/http

The HTTP inbound adapters. Contains FastAPI `APIRouter` instances that map HTTP requests
to application use cases and services.

## Files

| File | Description |
|---|---|
| `auth_router.py` | Authentication route handlers; the `router` object included by `main.py` |
| `health_router.py` | Kubernetes health probe handlers |

## Registered routes

### Auth routes (`/api/v1/auth`)

| Method | Path | Handler | Description |
|---|---|---|---|
| `POST` | `/api/v1/auth/register` | `register` | Register a new user |
| `POST` | `/api/v1/auth/login` | `login` | Authenticate and return JWT tokens |
| `POST` | `/api/v1/auth/token` | `token` | OAuth2 password flow (alias for login) |
| `GET` | `/api/v1/auth/me` | `get_current_user` | Return the authenticated user's profile |

### Health routes

| Method | Path | Handler | Tags |
|---|---|---|---|
| `GET` | `/health` | `health_check` | Health |
| `GET` | `/health/live` | `liveness_probe` | Probes |
| `GET` | `/livez` | `liveness_probe` *(alias)* | — |
| `GET` | `/healthz` | `liveness_probe` *(alias)* | — |
| `GET` | `/health/ready` | `readiness_probe` | Probes |
| `GET` | `/readyz` | `readiness_probe` *(alias)* | — |
| `GET` | `/readiness` | `readiness_probe` *(alias)* | — |
| `GET` | `/health/startup` | `startup_probe` | Probes |
| `GET` | `/startupz` | `startup_probe` *(alias)* | — |

Alias routes are registered with `include_in_schema=False` so they appear in Kubernetes
manifests but not in the OpenAPI/Swagger UI.

## Design notes

- Route handlers contain **no business logic** — they translate, delegate, and map errors.
- All dependencies are injected via `Annotated[T, Depends(factory)]`.
- The router has no direct knowledge of concrete adapters or infrastructure classes.

See `../../README.md` for the full adapters layer overview.
