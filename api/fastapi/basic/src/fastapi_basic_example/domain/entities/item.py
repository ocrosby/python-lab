"""Item entity."""

from dataclasses import dataclass


@dataclass
class Item:
    """Item entity representing a business item."""

    item_id: int
    name: str | None = None
    description: str | None = None

    def __post_init__(self):
        """Validate entity after initialization."""
        if self.item_id <= 0:
            raise ValueError("Item ID must be positive")

    def update_name(self, name: str) -> None:
        """Update item name."""
        if not name or not name.strip():
            raise ValueError("Name cannot be empty")
        self.name = name.strip()

    def update_description(self, description: str) -> None:
        """Update item description."""
        self.description = description.strip() if description else None
