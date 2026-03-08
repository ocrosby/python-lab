"""Datetime utilities for consistent timestamp handling."""

from datetime import UTC, datetime


def current_utc_timestamp() -> str:
    """Get current UTC timestamp in ISO format."""
    return datetime.now(UTC).isoformat()
