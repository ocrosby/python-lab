"""Tests for Result pattern."""

from fastapi_basic_example.domain.result import Failure, Success


def test_success_creation():
    """Test creating a success result."""
    result = Success(value=42)
    assert result.value == 42


def test_success_is_success():
    """Test is_success method."""
    result = Success(value="test")
    assert result.is_success() is True


def test_success_is_failure():
    """Test is_failure method."""
    result = Success(value="test")
    assert result.is_failure() is False


def test_success_with_string_value():
    """Test success with string value."""
    result = Success(value="Hello World")
    assert result.value == "Hello World"
    assert result.is_success()


def test_success_with_dict_value():
    """Test success with dict value."""
    result = Success(value={"key": "value"})
    assert result.value == {"key": "value"}
    assert result.is_success()


def test_success_with_none_value():
    """Test success with None value."""
    result = Success(value=None)
    assert result.value is None
    assert result.is_success()


def test_success_immutability():
    """Test that success is frozen."""
    result = Success(value=42)
    assert result.value == 42


def test_failure_creation():
    """Test creating a failure result."""
    result = Failure(error="Something went wrong")
    assert result.error == "Something went wrong"


def test_failure_is_success():
    """Test is_success method."""
    result = Failure(error="Error")
    assert result.is_success() is False


def test_failure_is_failure():
    """Test is_failure method."""
    result = Failure(error="Error")
    assert result.is_failure() is True


def test_failure_with_exception():
    """Test failure with exception."""
    exception = ValueError("Invalid value")
    result = Failure(error=exception)
    assert result.error == exception
    assert result.is_failure()


def test_failure_with_custom_error_object():
    """Test failure with custom error object."""
    error = {"code": 404, "message": "Not found"}
    result = Failure(error=error)
    assert result.error == error
    assert result.is_failure()


def test_failure_immutability():
    """Test that failure is frozen."""
    result = Failure(error="Error")
    assert result.error == "Error"


def test_result_can_be_success_or_failure():
    """Test that Result can be either Success or Failure."""

    def divide(a: int, b: int) -> Success[int] | Failure[str]:
        if b == 0:
            return Failure(error="Division by zero")
        return Success(value=a // b)

    success_result = divide(10, 2)
    assert success_result.is_success()
    assert isinstance(success_result, Success)

    failure_result = divide(10, 0)
    assert failure_result.is_failure()
    assert isinstance(failure_result, Failure)


def test_pattern_matching_with_result():
    """Test pattern matching with Result."""

    def divide(a: int, b: int) -> Success[int] | Failure[str]:
        if b == 0:
            return Failure(error="Division by zero")
        return Success(value=a // b)

    result = divide(10, 2)
    if isinstance(result, Success):
        assert result.value == 5
    elif isinstance(result, Failure):
        raise AssertionError("Should not be a failure")

    result = divide(10, 0)
    if isinstance(result, Success):
        raise AssertionError("Should not be a success")
    elif isinstance(result, Failure):
        assert result.error == "Division by zero"
