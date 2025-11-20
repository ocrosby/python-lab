"""Tests for logging middleware."""

from unittest.mock import patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.fastapi_basic_example.infrastructure.logging.middleware import (
    RequestLoggingMiddleware,
)


@pytest.fixture
def app_with_middleware():
    """Create a FastAPI app with logging middleware for testing."""
    app = FastAPI()
    app.add_middleware(RequestLoggingMiddleware)

    @app.get("/test")
    async def test_endpoint():
        return {"message": "test"}

    @app.get("/error")
    async def error_endpoint():
        raise ValueError("Test error")

    return app


@pytest.fixture
def client_with_middleware(app_with_middleware):
    """Create test client with middleware."""
    return TestClient(app_with_middleware)


@patch("src.fastapi_basic_example.infrastructure.logging.middleware.logger")
def test_request_logging_success(mock_logger, client_with_middleware):
    """Test that successful requests are logged correctly."""
    response = client_with_middleware.get("/test")

    assert response.status_code == 200
    assert "X-Request-ID" in response.headers

    # Check that logger.info was called for request start and completion
    assert mock_logger.info.call_count == 2

    # Check the first call (request started)
    first_call = mock_logger.info.call_args_list[0]
    assert "Request started" in first_call[0]
    assert "request_id" in first_call[1]
    assert "method" in first_call[1]
    assert "path" in first_call[1]
    assert first_call[1]["method"] == "GET"
    assert first_call[1]["path"] == "/test"

    # Check the second call (request completed)
    second_call = mock_logger.info.call_args_list[1]
    assert "Request completed" in second_call[0]
    assert "status_code" in second_call[1]
    assert "processing_time_ms" in second_call[1]
    assert second_call[1]["status_code"] == 200


@patch("src.fastapi_basic_example.infrastructure.logging.middleware.logger")
def test_request_logging_error(mock_logger, client_with_middleware):
    """Test that failed requests are logged correctly."""
    with pytest.raises(ValueError, match="Test error"):
        client_with_middleware.get("/error")

    mock_logger.info.assert_called_once()
    mock_logger.error.assert_called_once()

    error_call = mock_logger.error.call_args
    assert "Request failed" in error_call[0]
    assert "error" in error_call[1]
    assert "error_type" in error_call[1]
    assert error_call[1]["error_type"] == "ValueError"


def test_request_id_in_response_headers(client_with_middleware):
    """Test that request ID is added to response headers."""
    response = client_with_middleware.get("/test")

    assert response.status_code == 200
    assert "X-Request-ID" in response.headers

    request_id = response.headers["X-Request-ID"]
    assert len(request_id) > 0  # Should have a UUID


@patch("src.fastapi_basic_example.infrastructure.logging.middleware.set_request_id")
def test_request_id_context(mock_set_request_id, client_with_middleware):
    """Test that request ID is set in context."""
    response = client_with_middleware.get("/test")

    assert response.status_code == 200
    mock_set_request_id.assert_called_once()

    # The argument should be a UUID string
    request_id = mock_set_request_id.call_args[0][0]
    assert isinstance(request_id, str)
    assert len(request_id.split("-")) == 5  # UUID format
