"""Query parameters value object."""

from pydantic import BaseModel, ConfigDict, field_validator


class QueryParams(BaseModel):
    """Value object for query parameters."""

    model_config = ConfigDict(
        frozen=True,  # Immutable value object
        str_strip_whitespace=True,  # Auto-strip strings
    )

    q: str | None = None

    @field_validator("q")
    @classmethod
    def validate_query(cls, v: str | None) -> str | None:
        """Validate query parameter."""
        if v is not None and len(v.strip()) == 0:
            return None
        return v
