# domain/value_objects

Value objects are immutable domain types whose identity is defined entirely by their field
values, not by an ID. Two value objects with the same fields are equal.

Value objects enforce domain invariants at construction time and normalise their inputs so
that downstream code never has to guard against edge cases.

## Files

| File | Class | Description |
|---|---|---|
| `query_params.py` | `QueryParams` | Wraps the optional `q` query string parameter |

## QueryParams

```python
class QueryParams(BaseModel):
    model_config = ConfigDict(frozen=True, str_strip_whitespace=True)
    q: str | None = None
```

**Invariant:** empty or whitespace-only strings are normalised to `None` by a
`field_validator`, so callers never encounter `q == ""`.

**Why not use `str | None` directly?**
Wrapping the parameter in a named type makes the intent explicit at call sites, enforces
the normalisation invariant in a single location, and makes it easy to extend the value
object with additional query parameters in the future.

## Adding a new value object

1. Create `domain/value_objects/<name>.py` with a frozen Pydantic `BaseModel`.
2. Add `field_validator`s for any normalisation or invariant enforcement.
3. Use `ConfigDict(frozen=True)` to guarantee immutability.

See `../README.md` for the full domain layer overview.
