"""Time provider utilities for dependency injection."""

import time
from abc import ABC, abstractmethod
from datetime import UTC, datetime


class TimeProvider(ABC):
    """Abstract base class for time providers."""

    @abstractmethod
    def now(self) -> datetime:
        """Get current datetime."""
        pass

    @abstractmethod
    def time(self) -> float:
        """Get current time as float (seconds since epoch)."""
        pass


class SystemTimeProvider(TimeProvider):
    """System time provider using real datetime."""

    def now(self) -> datetime:
        """Get current UTC datetime."""
        return datetime.now(UTC)

    def time(self) -> float:
        """Get current time as float."""
        return time.time()
