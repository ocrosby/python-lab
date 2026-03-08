# infrastructure/decorators

Cross-cutting decorators applied at the application layer boundary. Decorators here add
behaviour (logging, timing, tracing) to functions without modifying their business logic.

## Files

| File | Decorator | Description |
|---|---|---|
| `logging.py` | `@log_execution(layer)` | Logs entry, exit, and errors for async and sync functions |

## @log_execution(layer)

```python
@log_execution("use_cases")
async def execute(self, item_id: int, ...) -> ItemResponseDTO:
    ...
```

**On entry:** logs `"Executing {func_name}"` at INFO level.
**On success:** logs `"Completed {func_name}"` at INFO level.
**On exception:** logs `"Failed {func_name}"` at ERROR level with `error` and
`error_type` fields, then re-raises the exception unchanged.

All log entries include `request_id` from the current `ContextVar` context (set by
`RequestIDMiddleware`), so every use-case invocation is traceable to its originating
request.

The decorator inspects `inspect.iscoroutinefunction(func)` and wraps with `async_wrapper`
or `sync_wrapper` accordingly, so it is safe to apply to both async and sync functions.

## Usage guidance

Apply `@log_execution` at use-case and service method boundaries — not deep inside domain
logic. The goal is observability at the orchestration layer, not per-line tracing.

See `../README.md` for the full infrastructure layer overview.
