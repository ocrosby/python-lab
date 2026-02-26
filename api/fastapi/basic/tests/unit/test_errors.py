"""Tests for domain errors."""

from fastapi_basic_example.domain.errors import (
    DomainError,
    ItemNotFoundError,
    ValidationError,
)


def test_domain_error_creation():
    """Test creating a domain error."""
    error = DomainError(message="Something went wrong")
    assert error.message == "Something went wrong"


def test_domain_error_string_representation():
    """Test string representation of domain error."""
    error = DomainError(message="Something went wrong")
    assert str(error) == "Something went wrong"


def test_domain_error_immutability():
    """Test that domain error is frozen."""
    error = DomainError(message="Something went wrong")
    assert error.message == "Something went wrong"


def test_item_not_found_error_creation():
    """Test creating an item not found error."""
    error = ItemNotFoundError(message="", item_id=42)
    assert error.item_id == 42
    assert error.message == "Item 42 not found"


def test_item_not_found_error_string_representation():
    """Test string representation."""
    error = ItemNotFoundError(message="", item_id=123)
    assert str(error) == "Item 123 not found"


def test_item_not_found_error_different_ids():
    """Test errors with different IDs."""
    error1 = ItemNotFoundError(message="", item_id=1)
    error2 = ItemNotFoundError(message="", item_id=2)
    assert error1.message == "Item 1 not found"
    assert error2.message == "Item 2 not found"


def test_validation_error_creation():
    """Test creating a validation error."""
    error = ValidationError(message="", field="email")
    assert error.field == "email"
    assert error.message == "Validation failed for field: email"


def test_validation_error_string_representation():
    """Test string representation."""
    error = ValidationError(message="", field="username")
    assert str(error) == "Validation failed for field: username"


def test_validation_error_different_fields():
    """Test errors with different fields."""
    error1 = ValidationError(message="", field="email")
    error2 = ValidationError(message="", field="password")
    assert error1.message == "Validation failed for field: email"
    assert error2.message == "Validation failed for field: password"
