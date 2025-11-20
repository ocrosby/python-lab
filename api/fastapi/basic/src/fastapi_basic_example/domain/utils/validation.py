"""Common validation utilities."""


def validate_positive_id(value: int) -> int:
    """Validate that an ID is positive."""
    if value <= 0:
        raise ValueError("ID must be positive")
    return value


def validate_and_strip_string(value: str | None) -> str | None:
    """Validate and strip a string, returning None if empty."""
    if value is None:
        return None

    stripped = value.strip()
    if not stripped:
        return None
    return stripped


def validate_non_empty_string(value: str | None) -> str | None:
    """Validate that a string is not empty after stripping."""
    if value is None:
        return None

    stripped = value.strip()
    if not stripped:
        raise ValueError("String cannot be empty")
    return stripped
