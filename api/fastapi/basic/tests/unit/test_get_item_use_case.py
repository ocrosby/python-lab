"""Unit tests for GetItemUseCase."""

from unittest.mock import AsyncMock, MagicMock

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

        assert use_case.repository == mock_repo

    @pytest.mark.asyncio
    async def test_execute_item_found_without_query_params(self, mocker: MockerFixture):
        """Test executing use case when item is found without query params."""
        # Arrange
        mock_repo = mocker.MagicMock()
        item = Item(item_id=1, name="Test Item", description="Test Description")
        mock_repo.get_by_id = AsyncMock(return_value=item)

        use_case = GetItemUseCase(mock_repo)

        # Act
        result = await use_case.execute(1, None)

        # Assert
        assert isinstance(result, ItemResponseDTO)
        assert result.item_id == 1
        assert result.q is None
        mock_repo.get_by_id.assert_called_once_with(1)

    @pytest.mark.asyncio
    async def test_execute_item_found_with_query_params(self, mocker: MockerFixture):
        """Test executing use case when item is found with query params."""
        # Arrange
        mock_repo = mocker.MagicMock()
        item = Item(item_id=2, name="Test Item", description="Test Description")
        mock_repo.get_by_id = AsyncMock(return_value=item)

        query_params = QueryParams(q="test query")
        use_case = GetItemUseCase(mock_repo)

        # Act
        result = await use_case.execute(2, query_params)

        # Assert
        assert isinstance(result, ItemResponseDTO)
        assert result.item_id == 2
        assert result.q == "test query"
        mock_repo.get_by_id.assert_called_once_with(2)

    @pytest.mark.asyncio
    async def test_execute_item_not_found_creates_default(self, mocker: MockerFixture):
        """Test executing use case when item is not found creates default item."""
        # Arrange
        mock_repo = mocker.MagicMock()
        mock_repo.get_by_id = AsyncMock(return_value=None)

        use_case = GetItemUseCase(mock_repo)

        # Act
        result = await use_case.execute(999, None)

        # Assert
        assert isinstance(result, ItemResponseDTO)
        assert result.item_id == 999
        assert result.q is None
        mock_repo.get_by_id.assert_called_once_with(999)

    @pytest.mark.asyncio
    async def test_execute_item_not_found_with_query_params(
        self, mocker: MockerFixture
    ):
        """Test executing use case when item not found with query params."""
        # Arrange
        mock_repo = mocker.MagicMock()
        mock_repo.get_by_id = AsyncMock(return_value=None)

        query_params = QueryParams(q="not found query")
        use_case = GetItemUseCase(mock_repo)

        # Act
        result = await use_case.execute(404, query_params)

        # Assert
        assert isinstance(result, ItemResponseDTO)
        assert result.item_id == 404
        assert result.q == "not found query"
        mock_repo.get_by_id.assert_called_once_with(404)

    @pytest.mark.asyncio
    async def test_execute_repository_exception_propagated(self, mocker: MockerFixture):
        """Test that repository exceptions are properly propagated."""
        # Arrange
        mock_repo = mocker.MagicMock()
        mock_repo.get_by_id = AsyncMock(side_effect=Exception("Database error"))

        use_case = GetItemUseCase(mock_repo)

        # Act & Assert
        with pytest.raises(Exception, match="Database error"):
            await use_case.execute(1, None)

        mock_repo.get_by_id.assert_called_once_with(1)

    @pytest.mark.asyncio
    async def test_execute_with_empty_query_string(self, mocker: MockerFixture):
        """Test executing use case with empty query string."""
        # Arrange
        mock_repo = mocker.MagicMock()
        item = Item(item_id=5, name="Test Item", description="Test Description")
        mock_repo.get_by_id = AsyncMock(return_value=item)

        query_params = QueryParams(q="")
        use_case = GetItemUseCase(mock_repo)

        # Act
        result = await use_case.execute(5, query_params)

        # Assert
        assert isinstance(result, ItemResponseDTO)
        assert result.item_id == 5
        assert result.q == ""
