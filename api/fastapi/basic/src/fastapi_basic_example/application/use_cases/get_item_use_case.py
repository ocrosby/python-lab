"""Get item use case."""

from typing import Optional

from ...domain.repositories.item_repository import ItemRepository
from ...domain.value_objects.query_params import QueryParams
from ..dto.item_dto import ItemResponseDTO


class GetItemUseCase:
    """Use case for getting an item."""

    def __init__(self, item_repository: ItemRepository):
        self._item_repository = item_repository

    async def execute(
        self, item_id: int, query_params: Optional[QueryParams] = None
    ) -> ItemResponseDTO:
        """Execute the get item use case."""
        if item_id <= 0:
            raise ValueError("Item ID must be positive")

        # For this simple example, we'll just return the item_id and query
        # In a real implementation, you'd fetch from the repository
        q_value = query_params.q if query_params and query_params.has_query else None

        return ItemResponseDTO(item_id=item_id, q=q_value)
