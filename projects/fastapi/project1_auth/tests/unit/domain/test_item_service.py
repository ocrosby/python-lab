import pytest
from unittest.mock import Mock, MagicMock
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from service import ItemService, ItemNotFoundException
from models import Item, ItemInDB


@pytest.fixture
def mock_repository():
    return Mock()


@pytest.fixture
def item_service(mock_repository):
    return ItemService(mock_repository)


@pytest.fixture
def sample_item():
    return Item(name="Test Item", description="Test Description")


@pytest.fixture
def sample_item_in_db():
    return ItemInDB(id=1, name="Test Item", description="Test Description")


def test_create_item(item_service, mock_repository, sample_item, sample_item_in_db):
    mock_repository.create.return_value = sample_item_in_db
    
    result = item_service.create_item(sample_item)
    
    assert result == sample_item_in_db
    mock_repository.create.assert_called_once_with(sample_item)


def test_get_item_found(item_service, mock_repository, sample_item_in_db):
    mock_repository.get_by_id.return_value = sample_item_in_db
    
    result = item_service.get_item(1)
    
    assert result == sample_item_in_db
    mock_repository.get_by_id.assert_called_once_with(1)


def test_get_item_not_found(item_service, mock_repository):
    mock_repository.get_by_id.return_value = None
    
    with pytest.raises(ItemNotFoundException) as exc_info:
        item_service.get_item(1)
    
    assert "Item with id 1 not found" in str(exc_info.value)
    mock_repository.get_by_id.assert_called_once_with(1)


def test_get_all_items(item_service, mock_repository, sample_item_in_db):
    expected_items = [sample_item_in_db]
    mock_repository.get_all.return_value = expected_items
    
    result = item_service.get_all_items()
    
    assert result == expected_items
    mock_repository.get_all.assert_called_once()


def test_update_item_found(item_service, mock_repository, sample_item, sample_item_in_db):
    mock_repository.update.return_value = sample_item_in_db
    
    result = item_service.update_item(1, sample_item)
    
    assert result == sample_item_in_db
    mock_repository.update.assert_called_once_with(1, sample_item)


def test_update_item_not_found(item_service, mock_repository, sample_item):
    mock_repository.update.return_value = None
    
    with pytest.raises(ItemNotFoundException) as exc_info:
        item_service.update_item(1, sample_item)
    
    assert "Item with id 1 not found" in str(exc_info.value)
    mock_repository.update.assert_called_once_with(1, sample_item)


def test_delete_item_found(item_service, mock_repository):
    mock_repository.delete.return_value = True
    
    item_service.delete_item(1)
    
    mock_repository.delete.assert_called_once_with(1)


def test_delete_item_not_found(item_service, mock_repository):
    mock_repository.delete.return_value = False
    
    with pytest.raises(ItemNotFoundException) as exc_info:
        item_service.delete_item(1)
    
    assert "Item with id 1 not found" in str(exc_info.value)
    mock_repository.delete.assert_called_once_with(1)
