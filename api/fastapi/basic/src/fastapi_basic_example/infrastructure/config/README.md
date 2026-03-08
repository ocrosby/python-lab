# infrastructure/config

Application configuration loaded from environment variables and `.env` files using
Pydantic `BaseSettings`.

## Files

| File | Class | Description |
|---|---|---|
| `settings.py` | `Settings` | All runtime configuration for the application |

## Settings fields

| Field | Type | Default | Description |
|---|---|---|---|
| `app_name` | `str` | `"FastAPI Basic Example"` | Application display name |
| `app_version` | `str` | `"1.0.0"` | Application version |
| `host` | `str` | `"0.0.0.0"` | Bind address for uvicorn |
| `port` | `int` | `8000` | Bind port (validated 1–65535) |
| `reload` | `bool` | `True` | Enable uvicorn hot reload |
| `log_level` | `str` | `"INFO"` | Log level (DEBUG/INFO/WARNING/ERROR/CRITICAL) |
| `json_logging` | `bool` | `False` | Emit JSON log lines (for production aggregation) |
| `cors_origins` | `list[str]` | `["http://localhost:3000", ...]` | CORS allowed origins |
| `cors_allow_credentials` | `bool` | `True` | CORS credentials policy |
| `cors_allow_methods` | `list[str]` | `["*"]` | CORS allowed methods |
| `cors_allow_headers` | `list[str]` | `["*"]` | CORS allowed headers |
| `allowed_hosts` | `list[str]` | `["localhost", "127.0.0.1", ...]` | Trusted host whitelist |
| `gzip_minimum_size` | `int` | `1000` | Min response bytes before GZip compression |
| `gzip_compression_level` | `int` | `5` | GZip compression level (1–9) |

## Validators

- `log_level` is upper-cased and must be one of `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`.
- `port` must be in the range 1–65535.

## Loading order

Pydantic `BaseSettings` resolves values in this order (highest priority first):
1. Environment variables (e.g. `export LOG_LEVEL=DEBUG`)
2. `.env` file in the working directory
3. Field defaults

Field names are case-insensitive (`LOG_LEVEL` matches `log_level`).

See `../README.md` for the full infrastructure layer overview.
