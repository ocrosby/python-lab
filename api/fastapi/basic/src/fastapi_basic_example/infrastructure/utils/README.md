# infrastructure/utils

Small utility classes and functions used across the application. All utilities are
abstracted behind interfaces to support dependency injection and testing.

## Files

| File | Abstractions | Concrete implementations |
|---|---|---|
| `id_generator.py` | `IdGenerator` | `UuidGenerator` |
| `time_provider.py` | `TimeProvider` | `SystemTimeProvider` |
| `datetime_utils.py` | — | `current_utc_timestamp()` |

---

## id_generator.py

```python
class IdGenerator(ABC):
    @abstractmethod
    def generate(self) -> str: ...

class UuidGenerator(IdGenerator):
    def generate(self) -> str:
        return str(uuid.uuid4())
```

Used by `RequestIDMiddleware` to generate per-request trace IDs. Injected via
`get_id_generator()` in the DI container so tests can substitute a deterministic
generator.

---

## time_provider.py

```python
class TimeProvider(ABC):
    @abstractmethod
    def time(self) -> float: ...

class SystemTimeProvider(TimeProvider):
    def time(self) -> float:
        return time.time()
```

Used by `TimingMiddleware` to measure request duration. Injected via `get_time_provider()`
so tests can inject a fixed time and assert on the `X-Process-Time` header value.

---

## datetime_utils.py

```python
def current_utc_timestamp() -> str:
    return datetime.now(UTC).isoformat()
```

Returns the current UTC time as an ISO 8601 string. Used by `HealthService` and the probe
response factory in `routers.py`. Isolated here so tests can monkeypatch a single location
to control timestamp output.

See `../README.md` for the full infrastructure layer overview.
