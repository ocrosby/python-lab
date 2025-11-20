"""Unit tests for domain entities."""

import pytest

from src.fastapi_basic_example.domain.entities.item import Item


@pytest.mark.unit
class TestItem:
    """Test cases for Item entity."""

    def test_item_creation_with_all_fields(self):
        """Test creating an item with all fields."""
        item = Item(item_id=1, name="Test Item", description="Test Description")

        assert item.item_id == 1
        assert item.name == "Test Item"
        assert item.description == "Test Description"

    def test_item_creation_with_minimal_fields(self):
        """Test creating an item with minimal required fields."""
        item = Item(item_id=42)

        assert item.item_id == 42
        assert item.name is None
        assert item.description is None

    def test_item_creation_with_name_only(self):
        """Test creating an item with ID and name only."""
        item = Item(item_id=5, name="Named Item")

        assert item.item_id == 5
        assert item.name == "Named Item"
        assert item.description is None

    def test_item_post_init_validation(self):
        """Test item post-initialization validation."""
        # This should not raise any exceptions
        item = Item(item_id=1, name="Valid Item", description="Valid Description")
        assert item.item_id == 1

        # Test with negative ID - should still work as it's just data
        item_negative = Item(item_id=-1, name="Negative ID Item")
        assert item_negative.item_id == -1

    def test_item_equality(self):
        """Test item equality comparison."""
        item1 = Item(item_id=1, name="Test", description="Description")
        item2 = Item(item_id=1, name="Test", description="Description")
        item3 = Item(item_id=2, name="Test", description="Description")

        assert item1 == item2
        assert item1 != item3

    def test_item_string_representation(self):
        """Test item string representation."""
        item = Item(item_id=1, name="Test Item", description="Test Description")
        str_repr = str(item)

        assert "Item" in str_repr
        assert "1" in str_repr
