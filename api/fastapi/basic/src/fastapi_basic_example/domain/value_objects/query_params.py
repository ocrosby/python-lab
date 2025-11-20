"""Query parameters value object."""

from dataclasses import dataclass


@dataclass(frozen=True)
class QueryParams:
    """Value object for query parameters."""

    q: str | None = None

    def __post_init__(self):
        """Validate query parameters."""
        if self.q is not None and len(self.q.strip()) == 0:
            object.__setattr__(self, "q", None)

    @property
    def has_query(self) -> bool:
        """Check if query parameter exists."""
        return self.q is not None
