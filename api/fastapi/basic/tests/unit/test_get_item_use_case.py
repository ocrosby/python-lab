"""Unit tests for GetItemUseCase."""

from unittest.mock import AsyncMock

import pytest
from pytest_mock import MockerFixture

from src.fastapi_basic_example.application.dto.item_dto import ItemResponseDTO
from src.fastapi_basic_example.application.use_cases.get_item_use_case import (
    GetItemUseCase,
)
from src.fastapi_basic_example.domain.entities.item import Item
from src.fastapi_basic_example.domain.errors import ItemNotFoundError
from src.fastapi_basic_example.domain.value_objects.query_params import QueryParams


@pytest.mark.unit
class TestGetItemUseCase:
    """Test cases for GetItemUseCase."""

    def test_init(self, mocker: MockerFixture):
        """Test use case initialization."""
        mock_repo = mocker.MagicMock()
        use_case = GetItemUseCase(mock_repo)

        assert use_case._item_repository == mock_repo

    @pytest.mark.asyncio
    async def test_execute_item_found_without_query_params(self, mocker: MockerFixture):
        """Test executing use case without query params."""
        mock_repo = mocker.MagicMock()
        mock_repo.get_by_id = AsyncMock(return_value=Item(item_id=1))
        use_case = GetItemUseCase(mock_repo)

        result = await use_case.execute(1, None)

        assert isinstance(result, ItemResponseDTO)
        assert result.item_id == 1
        assert result.q is None

    @pytest.mark.asyncio
    async def test_execute_item_found_with_query_params(self, mocker: MockerFixture):
        """Test executing use case with query params."""
        mock_repo = mocker.MagicMock()
        mock_repo.get_by_id = AsyncMock(return_value=Item(item_id=2))
        query_params = QueryParams(q="test query")
        use_case = GetItemUseCase(mock_repo)

        result = await use_case.execute(2, query_params)

        assert isinstance(result, ItemResponseDTO)
        assert result.item_id == 2
        assert result.q == "test query"

    @pytest.mark.asyncio
    async def test_execute_item_not_found_raises_error(self, mocker: MockerFixture):
        """Test executing use case raises ItemNotFoundError when item doesn't exist."""
        mock_repo = mocker.MagicMock()
        mock_repo.get_by_id = AsyncMock(return_value=None)
        use_case = GetItemUseCase(mock_repo)

        with pytest.raises(ItemNotFoundError) as exc_info:
            await use_case.execute(999, None)

        assert exc_info.value.item_id == 999

    @pytest.mark.asyncio
    async def test_execute_item_not_found_with_query_params(
        self, mocker: MockerFixture
    ):
        """Test executing use case raises ItemNotFoundError with query params."""
        mock_repo = mocker.MagicMock()
        mock_repo.get_by_id = AsyncMock(return_value=None)
        query_params = QueryParams(q="not found query")
        use_case = GetItemUseCase(mock_repo)

        with pytest.raises(ItemNotFoundError) as exc_info:
            await use_case.execute(404, query_params)

        assert exc_info.value.item_id == 404

    @pytest.mark.asyncio
    async def test_execute_repository_exception_propagated(self, mocker: MockerFixture):
        """Test that repository exceptions propagate through the use case."""
        mock_repo = mocker.MagicMock()
        mock_repo.get_by_id = AsyncMock(side_effect=RuntimeError("DB connection failed"))
        use_case = GetItemUseCase(mock_repo)

        with pytest.raises(RuntimeError, match="DB connection failed"):
            await use_case.execute(1, None)

    @pytest.mark.asyncio
    async def test_execute_with_empty_query_string(self, mocker: MockerFixture):
        """Test executing use case with empty query string."""
        mock_repo = mocker.MagicMock()
        mock_repo.get_by_id = AsyncMock(return_value=Item(item_id=5))
        query_params = QueryParams(q="")
        use_case = GetItemUseCase(mock_repo)

        result = await use_case.execute(5, query_params)

        assert isinstance(result, ItemResponseDTO)
        assert result.item_id == 5
        assert result.q is None
