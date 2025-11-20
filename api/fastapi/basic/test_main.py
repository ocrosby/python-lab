"""Tests for the FastAPI application."""

import pytest
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_read_root():
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"Hello": "World"}


def test_read_item():
    """Test the items endpoint."""
    response = client.get("/items/5?q=somequery")
    assert response.status_code == 200
    assert response.json() == {"item_id": 5, "q": "somequery"}


def test_read_item_without_query():
    """Test the items endpoint without query parameter."""
    response = client.get("/items/10")
    assert response.status_code == 200
    assert response.json() == {"item_id": 10, "q": None}


def test_health_check():
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}
