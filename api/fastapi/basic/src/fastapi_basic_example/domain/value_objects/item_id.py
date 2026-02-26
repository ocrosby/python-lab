"""Item ID value object."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ItemId:
    """Value object for Item ID."""

    value: int

    def __post_init__(self):
        """Validate item ID."""
        if self.value <= 0:
            raise ValueError("ItemId must be positive")

    def __int__(self) -> int:
        """Convert to int."""
        return self.value

    def __str__(self) -> str:
        """Convert to string."""
        return str(self.value)

    def __eq__(self, other) -> bool:
        """Compare equality."""
        if isinstance(other, ItemId):
            return self.value == other.value
        if isinstance(other, int):
            return self.value == other
        return False

    def __hash__(self) -> int:
        """Hash value."""
        return hash(self.value)
