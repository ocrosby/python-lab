"""Datetime utilities for consistent timestamp handling."""

from datetime import UTC, datetime


def current_utc_timestamp() -> str:
    """Get current UTC timestamp in ISO format."""
    return datetime.now(UTC).isoformat()


def current_utc_datetime() -> datetime:
    """Get current UTC datetime object."""
    return datetime.now(UTC)
