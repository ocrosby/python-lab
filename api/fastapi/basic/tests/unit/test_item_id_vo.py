"""Tests for ItemId value object."""

import pytest

from fastapi_basic_example.domain.value_objects.item_id import ItemId


def test_item_id_creation():
    """Test creating an item ID."""
    item_id = ItemId(value=42)
    assert item_id.value == 42


def test_item_id_validation_positive():
    """Test validation accepts positive values."""
    item_id = ItemId(value=1)
    assert item_id.value == 1


def test_item_id_validation_zero():
    """Test validation rejects zero."""
    with pytest.raises(ValueError, match="ItemId must be positive"):
        ItemId(value=0)


def test_item_id_validation_negative():
    """Test validation rejects negative values."""
    with pytest.raises(ValueError, match="ItemId must be positive"):
        ItemId(value=-1)


def test_item_id_validation_large_negative():
    """Test validation rejects large negative values."""
    with pytest.raises(ValueError, match="ItemId must be positive"):
        ItemId(value=-999)


def test_int_conversion():
    """Test converting to int."""
    item_id = ItemId(value=42)
    assert int(item_id) == 42
    assert isinstance(int(item_id), int)


def test_string_representation():
    """Test string representation."""
    item_id = ItemId(value=123)
    assert str(item_id) == "123"


def test_equality_with_item_id():
    """Test equality comparison with another ItemId."""
    item_id1 = ItemId(value=42)
    item_id2 = ItemId(value=42)
    item_id3 = ItemId(value=99)

    assert item_id1 == item_id2
    assert item_id1 != item_id3


def test_equality_with_int():
    """Test equality comparison with int."""
    item_id = ItemId(value=42)
    assert item_id == 42
    assert item_id != 99


def test_equality_with_other_types():
    """Test equality comparison with other types."""
    item_id = ItemId(value=42)
    assert item_id != "42"
    assert item_id != 42.0
    assert item_id is not None


def test_hash():
    """Test hash function."""
    item_id1 = ItemId(value=42)
    item_id2 = ItemId(value=42)
    item_id3 = ItemId(value=99)

    assert hash(item_id1) == hash(item_id2)
    assert hash(item_id1) != hash(item_id3)


def test_use_in_set():
    """Test using ItemId in a set."""
    item_id1 = ItemId(value=1)
    item_id2 = ItemId(value=2)
    item_id3 = ItemId(value=1)

    item_set = {item_id1, item_id2, item_id3}
    assert len(item_set) == 2


def test_use_as_dict_key():
    """Test using ItemId as dictionary key."""
    item_id1 = ItemId(value=1)
    item_id2 = ItemId(value=2)

    data = {item_id1: "first", item_id2: "second"}
    assert data[item_id1] == "first"
    assert data[ItemId(value=1)] == "first"


def test_immutability():
    """Test that item ID is frozen."""
    item_id = ItemId(value=42)
    assert item_id.value == 42
