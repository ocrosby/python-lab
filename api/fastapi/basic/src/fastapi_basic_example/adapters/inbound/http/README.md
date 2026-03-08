# adapters/inbound/http

The HTTP inbound adapter. Contains a single FastAPI `APIRouter` that maps HTTP requests to
application use cases and services.

## Files

| File | Description |
|---|---|
| `routers.py` | All route handlers; the `router` object imported by `main.py` |

## Registered routes

| Method | Path | Handler | Tags |
|---|---|---|---|
| `GET` | `/` | `read_root` | — |
| `GET` | `/items/{item_id}` | `read_item` | — |
| `GET` | `/health` | `health_check` | Health |
| `GET` | `/health/live` | `liveness_probe` | Probes |
| `GET` | `/healthz` | `liveness_probe` *(alias)* | — |
| `GET` | `/health/ready` | `readiness_probe` | Probes |
| `GET` | `/readiness` | `readiness_probe` *(alias)* | — |
| `GET` | `/health/startup` | `startup_probe` | Probes |

Alias routes (`/healthz`, `/readiness`) are registered with `include_in_schema=False` so
they appear in Kubernetes manifests but not in the OpenAPI/Swagger UI.

## Design notes

- Route handlers contain **no business logic** — they translate, delegate, and map errors.
- `ItemNotFoundError` → HTTP 404; service unavailable states → HTTP 503.
- All dependencies are injected via `Annotated[T, Depends(factory)]`; the router has no
  direct knowledge of concrete adapters or infrastructure classes.

See `../../README.md` for the full adapters layer overview.
