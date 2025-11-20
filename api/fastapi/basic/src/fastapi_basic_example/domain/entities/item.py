"""Item entity."""

from pydantic import BaseModel, ConfigDict, Field, field_validator


class Item(BaseModel):
    """Item entity representing a business item."""

    model_config = ConfigDict(
        validate_assignment=True,  # Validate on field assignment
        str_strip_whitespace=True,  # Auto-strip strings
    )

    item_id: int = Field(..., gt=0, description="Item ID must be positive")
    name: str | None = None
    description: str | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, v):
        """Validate name field."""
        if v is not None and not v.strip():
            raise ValueError("Name cannot be empty")
        return v.strip() if v else None

    @field_validator("description")
    @classmethod
    def validate_description(cls, v):
        """Validate description field."""
        return v.strip() if v else None

    def update_name(self, name: str) -> None:
        """Update item name."""
        # Validation handled by Pydantic automatically due to validate_assignment=True
        self.name = name

    def update_description(self, description: str) -> None:
        """Update item description."""
        # Validation handled by Pydantic automatically due to validate_assignment=True
        self.description = description
