"""ID generation utilities for dependency injection."""

import uuid
from abc import ABC, abstractmethod


class IdGenerator(ABC):
    """Abstract base class for ID generators."""

    @abstractmethod
    def generate(self) -> str:
        """Generate a unique ID."""
        pass


class UuidGenerator(IdGenerator):
    """UUID-based ID generator."""

    def generate(self) -> str:
        """Generate a UUID4 string."""
        return str(uuid.uuid4())
