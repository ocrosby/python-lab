"""Tests for command pattern base classes."""

import pytest

from fastapi_basic_example.application.commands.base import Command, Query
from fastapi_basic_example.domain.result import Failure, Success


@pytest.mark.asyncio
async def test_command_interface():
    """Test command implementation."""

    class AddNumbersCommand(Command[tuple[int, int], int, str]):
        async def execute(
            self, request: tuple[int, int]
        ) -> Success[int] | Failure[str]:
            a, b = request
            if a < 0 or b < 0:
                return Failure(error="Negative numbers not allowed")
            return Success(value=a + b)

    command = AddNumbersCommand()
    result = await command.execute((2, 3))

    assert result.is_success()
    assert isinstance(result, Success)
    assert result.value == 5


@pytest.mark.asyncio
async def test_command_failure():
    """Test command failure case."""

    class AddNumbersCommand(Command[tuple[int, int], int, str]):
        async def execute(
            self, request: tuple[int, int]
        ) -> Success[int] | Failure[str]:
            a, b = request
            if a < 0 or b < 0:
                return Failure(error="Negative numbers not allowed")
            return Success(value=a + b)

    command = AddNumbersCommand()
    result = await command.execute((-1, 3))

    assert result.is_failure()
    assert isinstance(result, Failure)
    assert result.error == "Negative numbers not allowed"


@pytest.mark.asyncio
async def test_query_interface():
    """Test query implementation."""

    class GetUserQuery(Query[int, str, str]):
        async def execute(self, request: int) -> Success[str] | Failure[str]:
            if request == 1:
                return Success(value="John Doe")
            return Failure(error="User not found")

    query = GetUserQuery()
    result = await query.execute(1)

    assert result.is_success()
    assert isinstance(result, Success)
    assert result.value == "John Doe"


@pytest.mark.asyncio
async def test_query_failure():
    """Test query failure case."""

    class GetUserQuery(Query[int, str, str]):
        async def execute(self, request: int) -> Success[str] | Failure[str]:
            if request == 1:
                return Success(value="John Doe")
            return Failure(error="User not found")

    query = GetUserQuery()
    result = await query.execute(999)

    assert result.is_failure()
    assert isinstance(result, Failure)
    assert result.error == "User not found"
