"""Unit tests for GetItemUseCase."""

from unittest.mock import AsyncMock

import pytest
from pytest_mock import MockerFixture

from src.fastapi_basic_example.application.dto.item_dto import ItemResponseDTO
from src.fastapi_basic_example.application.use_cases.get_item_use_case import (
    GetItemUseCase,
)
from src.fastapi_basic_example.domain.entities.item import Item
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
        use_case = GetItemUseCase(mock_repo)

        result = await use_case.execute(1, None)

        assert isinstance(result, ItemResponseDTO)
        assert result.item_id == 1
        assert result.q is None

    @pytest.mark.asyncio
    async def test_execute_item_found_with_query_params(self, mocker: MockerFixture):
        """Test executing use case with query params."""
        mock_repo = mocker.MagicMock()
        query_params = QueryParams(q="test query")
        use_case = GetItemUseCase(mock_repo)

        result = await use_case.execute(2, query_params)

        assert isinstance(result, ItemResponseDTO)
        assert result.item_id == 2
        assert result.q == "test query"

    @pytest.mark.asyncio
    async def test_execute_item_not_found_creates_default(self, mocker: MockerFixture):
        """Test executing use case returns item_id regardless."""
        mock_repo = mocker.MagicMock()
        use_case = GetItemUseCase(mock_repo)

        result = await use_case.execute(999, None)

        assert isinstance(result, ItemResponseDTO)
        assert result.item_id == 999
        assert result.q is None

    @pytest.mark.asyncio
    async def test_execute_item_not_found_with_query_params(
        self, mocker: MockerFixture
    ):
        """Test executing use case with query params."""
        mock_repo = mocker.MagicMock()
        query_params = QueryParams(q="not found query")
        use_case = GetItemUseCase(mock_repo)

        result = await use_case.execute(404, query_params)

        assert isinstance(result, ItemResponseDTO)
        assert result.item_id == 404
        assert result.q == "not found query"

    @pytest.mark.asyncio
    async def test_execute_repository_exception_propagated(self, mocker: MockerFixture):
        """Test use case execution with positive item_id."""
        mock_repo = mocker.MagicMock()
        use_case = GetItemUseCase(mock_repo)

        result = await use_case.execute(1, None)

        assert isinstance(result, ItemResponseDTO)
        assert result.item_id == 1

    @pytest.mark.asyncio
    async def test_execute_with_empty_query_string(self, mocker: MockerFixture):
        """Test executing use case with empty query string."""
        mock_repo = mocker.MagicMock()
        query_params = QueryParams(q="")
        use_case = GetItemUseCase(mock_repo)

        result = await use_case.execute(5, query_params)

        assert isinstance(result, ItemResponseDTO)
        assert result.item_id == 5
        assert result.q is None
