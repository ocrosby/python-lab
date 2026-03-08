"""Get item use case."""

from ...domain.errors import ItemNotFoundError
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
        item = await self._item_repository.get_by_id(item_id)
        if item is None:
            raise ItemNotFoundError(message="", item_id=item_id)

        q_value = query_params.q if query_params else None
        return ItemResponseDTO(item_id=item.item_id, q=q_value)
