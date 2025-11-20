"""Unit tests for domain value objects."""

import pytest

from src.fastapi_basic_example.domain.value_objects.query_params import QueryParams


@pytest.mark.unit
class TestQueryParams:
    """Test cases for QueryParams value object."""

    def test_query_params_creation_with_value(self):
        """Test creating QueryParams with a query value."""
        params = QueryParams(q="test query")

        assert params.q == "test query"

    def test_query_params_creation_without_value(self):
        """Test creating QueryParams without a query value."""
        params = QueryParams()

        assert params.q is None

    def test_query_params_creation_with_none(self):
        """Test creating QueryParams with explicit None."""
        params = QueryParams(q=None)

        assert params.q is None

    def test_query_params_creation_with_empty_string(self):
        """Test creating QueryParams with empty string."""
        params = QueryParams(q="")

        assert params.q == ""

    def test_query_params_post_init_validation(self):
        """Test QueryParams post-initialization validation."""
        # This should not raise any exceptions
        params = QueryParams(q="valid query")
        assert params.q == "valid query"

        # Test with whitespace
        params_whitespace = QueryParams(q="  whitespace query  ")
        assert params_whitespace.q == "  whitespace query  "

    def test_query_params_equality(self):
        """Test QueryParams equality comparison."""
        params1 = QueryParams(q="test")
        params2 = QueryParams(q="test")
        params3 = QueryParams(q="different")
        params4 = QueryParams(q=None)
        params5 = QueryParams()

        assert params1 == params2
        assert params1 != params3
        assert params4 == params5  # Both have q=None

    def test_query_params_string_representation(self):
        """Test QueryParams string representation."""
        params = QueryParams(q="test query")
        str_repr = str(params)

        assert "QueryParams" in str_repr
        assert "test query" in str_repr

    def test_query_params_with_special_characters(self):
        """Test QueryParams with special characters."""
        special_query = "test@#$%^&*()_+{}|:<>?[]\\;'\",./"
        params = QueryParams(q=special_query)

        assert params.q == special_query
