"""Time provider utilities for dependency injection."""

import time
from abc import ABC, abstractmethod


class TimeProvider(ABC):
    """Abstract base class for time providers."""

    @abstractmethod
    def time(self) -> float:
        """Get current time as float (seconds since epoch)."""
        pass


class SystemTimeProvider(TimeProvider):
    """System time provider using real datetime."""

    def time(self) -> float:
        """Get current time as float."""
        return time.time()
