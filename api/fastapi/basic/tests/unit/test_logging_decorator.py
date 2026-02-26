"""Tests for logging decorator."""

from unittest.mock import Mock, patch

import pytest

from fastapi_basic_example.infrastructure.decorators.logging import log_execution


@pytest.mark.asyncio
async def test_async_function_success():
    """Test decorator with successful async function."""
    mock_logger = Mock()

    @log_execution("test_logger")
    async def async_function(x: int, y: int) -> int:
        return x + y

    with patch("structlog.get_logger", return_value=mock_logger):
        result = await async_function(2, 3)

    assert result == 5
    assert mock_logger.info.call_count == 2


@pytest.mark.asyncio
async def test_async_function_failure():
    """Test decorator with failing async function."""
    mock_logger = Mock()

    @log_execution("test_logger")
    async def async_function() -> None:
        raise ValueError("Test error")

    with patch("structlog.get_logger", return_value=mock_logger):
        with pytest.raises(ValueError, match="Test error"):
            await async_function()

    assert mock_logger.info.call_count == 1
    assert mock_logger.error.call_count == 1


def test_sync_function_success():
    """Test decorator with successful sync function."""
    mock_logger = Mock()

    @log_execution("test_logger")
    def sync_function(x: int, y: int) -> int:
        return x * y

    with patch("structlog.get_logger", return_value=mock_logger):
        result = sync_function(3, 4)

    assert result == 12
    assert mock_logger.info.call_count == 2


def test_sync_function_failure():
    """Test decorator with failing sync function."""
    mock_logger = Mock()

    @log_execution("test_logger")
    def sync_function() -> None:
        raise RuntimeError("Sync error")

    with patch("structlog.get_logger", return_value=mock_logger):
        with pytest.raises(RuntimeError, match="Sync error"):
            sync_function()

    assert mock_logger.info.call_count == 1
    assert mock_logger.error.call_count == 1


@pytest.mark.asyncio
async def test_async_function_with_args_and_kwargs():
    """Test decorator preserves args and kwargs."""
    mock_logger = Mock()

    @log_execution("test_logger")
    async def async_function(a: int, b: int, c: int = 0) -> int:
        return a + b + c

    with patch("structlog.get_logger", return_value=mock_logger):
        result = await async_function(1, 2, c=3)

    assert result == 6


def test_sync_function_with_args_and_kwargs():
    """Test decorator preserves args and kwargs."""
    mock_logger = Mock()

    @log_execution("test_logger")
    def sync_function(a: int, b: int, c: int = 0) -> int:
        return a + b + c

    with patch("structlog.get_logger", return_value=mock_logger):
        result = sync_function(1, 2, c=3)

    assert result == 6


@pytest.mark.asyncio
async def test_logger_name_is_used():
    """Test that the logger name is used correctly."""

    @log_execution("custom_logger")
    async def async_function() -> str:
        return "test"

    with patch("structlog.get_logger") as mock_get_logger:
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        await async_function()
        mock_get_logger.assert_called_with("custom_logger")


def test_sync_logger_name_is_used():
    """Test that the logger name is used correctly for sync functions."""

    @log_execution("sync_logger")
    def sync_function() -> str:
        return "test"

    with patch("structlog.get_logger") as mock_get_logger:
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        sync_function()
        mock_get_logger.assert_called_with("sync_logger")


@pytest.mark.asyncio
async def test_function_metadata_preserved():
    """Test that function metadata is preserved."""

    @log_execution("test_logger")
    async def async_function_with_docstring() -> None:
        """This is a docstring."""
        pass

    assert async_function_with_docstring.__name__ == "async_function_with_docstring"
    assert async_function_with_docstring.__doc__ == "This is a docstring."


def test_sync_function_metadata_preserved():
    """Test that function metadata is preserved for sync functions."""

    @log_execution("test_logger")
    def sync_function_with_docstring() -> None:
        """This is a sync docstring."""
        pass

    assert sync_function_with_docstring.__name__ == "sync_function_with_docstring"
    assert sync_function_with_docstring.__doc__ == "This is a sync docstring."
