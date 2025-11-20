"""Item entity."""

from pydantic import BaseModel, ConfigDict, Field, field_validator


def _strip_or_none(value: str | None) -> str | None:
    """Strip whitespace from string or return None."""
    return value.strip() if value else None


class Item(BaseModel):
    """Item entity representing a business item."""

    model_config = ConfigDict(
        frozen=True,
        str_strip_whitespace=True,
    )

    item_id: int = Field(..., gt=0, description="Item ID must be positive")
    name: str | None = None
    description: str | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str | None) -> str | None:
        """Validate name field."""
        if v is not None and not v.strip():
            raise ValueError("Name cannot be empty")
        return _strip_or_none(v)

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: str | None) -> str | None:
        """Validate description field."""
        return _strip_or_none(v)
