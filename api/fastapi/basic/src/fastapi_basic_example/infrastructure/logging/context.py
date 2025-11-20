"""Logging context utilities."""

from contextvars import ContextVar
from typing import Optional

# Context variable for request ID
request_id_var: ContextVar[Optional[str]] = ContextVar("request_id", default=None)


def set_request_id(request_id: str) -> None:
    """Set the current request ID in context."""
    request_id_var.set(request_id)


def get_request_id() -> Optional[str]:
    """Get the current request ID from context."""
    return request_id_var.get()


def get_logger_context() -> dict:
    """Get current logging context."""
    context = {}
    request_id = get_request_id()
    if request_id:
        context["request_id"] = request_id
    return context
