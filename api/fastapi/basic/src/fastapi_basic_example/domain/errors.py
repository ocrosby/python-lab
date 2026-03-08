"""Domain errors."""


class DomainError(Exception):
    """Base domain error."""

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message

    def __str__(self) -> str:
        """String representation."""
        return self.message


class ItemNotFoundError(DomainError):
    """Error when item is not found."""

    def __init__(self, message: str = "", item_id: int = 0):
        self.item_id = item_id
        super().__init__(f"Item {item_id} not found")


class ValidationError(DomainError):
    """Error for validation failures."""

    def __init__(self, message: str = "", field: str = ""):
        self.field = field
        super().__init__(f"Validation failed for field: {field}")
