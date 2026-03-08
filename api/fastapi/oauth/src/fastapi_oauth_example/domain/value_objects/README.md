# domain/value_objects

Value objects represent domain concepts whose equality is based on their field values,
not object identity. They are immutable and self-validating.

## Files

| File | Class | Description |
|---|---|---|
| `email.py` | `Email` | Validates and normalises an email address |
| `user_id.py` | `UserId` | Typed wrapper around a UUID user identifier |

## Email

Wraps a raw email string and enforces basic format validity on construction. Normalises
to lowercase so `User@Example.COM` and `user@example.com` compare equal.

```python
email = Email("User@Example.COM")
str(email)  # → "user@example.com"
```

## UserId

A typed wrapper around `uuid.UUID` that prevents accidental use of raw UUIDs in places
expecting a user identifier.

```python
user_id = UserId(uuid.uuid4())
```
