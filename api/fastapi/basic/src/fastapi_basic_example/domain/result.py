"""Result pattern for explicit error handling."""

from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T")
E = TypeVar("E")


@dataclass(frozen=True)
class Success(Generic[T]):
    """Success result containing a value."""

    value: T

    def is_success(self) -> bool:
        """Check if result is success."""
        return True

    def is_failure(self) -> bool:
        """Check if result is failure."""
        return False


@dataclass(frozen=True)
class Failure(Generic[E]):
    """Failure result containing an error."""

    error: E

    def is_success(self) -> bool:
        """Check if result is success."""
        return False

    def is_failure(self) -> bool:
        """Check if result is failure."""
        return True


Result = Success[T] | Failure[E]
