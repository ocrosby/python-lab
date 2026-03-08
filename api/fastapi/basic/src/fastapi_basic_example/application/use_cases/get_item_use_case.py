"""Get item use case."""

from ...domain.value_objects.query_params import QueryParams
from ...infrastructure.decorators.logging import log_execution
from ...ports.outbound.item_repository import ItemRepository
from ..dto.item_dto import ItemResponseDTO


class GetItemUseCase:
    """Use case for getting an item."""

    def __init__(self, item_repository: ItemRepository):
        self._item_repository = item_repository

    @log_execution("use_cases")
    async def execute(
        self, item_id: int, query_params: QueryParams | None = None
    ) -> ItemResponseDTO:
        """Execute the get item use case."""
        # For this simple example, we'll just return the item_id and query
        # In a real implementation, you'd fetch from the repository
        q_value = query_params.q if query_params else None

        # ItemResponseDTO will validate item_id automatically via Pydantic
        return ItemResponseDTO(item_id=item_id, q=q_value)
