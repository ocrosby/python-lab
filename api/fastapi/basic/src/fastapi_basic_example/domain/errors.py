"""Domain errors."""

from dataclasses import dataclass


@dataclass(frozen=True)
class DomainError:
    """Base domain error."""

    message: str

    def __str__(self) -> str:
        """String representation."""
        return self.message


@dataclass(frozen=True)
class ItemNotFoundError(DomainError):
    """Error when item is not found."""

    item_id: int

    def __post_init__(self):
        """Initialize message."""
        object.__setattr__(self, "message", f"Item {self.item_id} not found")


@dataclass(frozen=True)
class ValidationError(DomainError):
    """Error for validation failures."""

    field: str

    def __post_init__(self):
        """Initialize message."""
        object.__setattr__(
            self, "message", f"Validation failed for field: {self.field}"
        )
