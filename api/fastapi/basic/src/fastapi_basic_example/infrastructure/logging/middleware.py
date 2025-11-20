"""Request logging middleware."""

import time
import uuid
from collections.abc import Callable
from contextlib import asynccontextmanager

import structlog
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from .context import set_request_id

logger = structlog.get_logger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging HTTP requests and responses."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process the request and log details."""
        # Generate request ID
        request_id = str(uuid.uuid4())
        set_request_id(request_id)

        # Add request ID to request state for access in handlers
        request.state.request_id = request_id

        # Start timing
        start_time = time.time()

        # Extract request details
        method = request.method
        url = str(request.url)
        path = request.url.path
        query_params = dict(request.query_params)
        client_ip = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")

        # Log incoming request
        logger.info(
            "Request started",
            request_id=request_id,
            method=method,
            url=url,
            path=path,
            query_params=query_params,
            client_ip=client_ip,
            user_agent=user_agent,
        )

        try:
            # Process the request
            response = await call_next(request)
        except Exception as exc:
            # Log error
            processing_time = time.time() - start_time
            logger.error(
                "Request failed",
                request_id=request_id,
                method=method,
                path=path,
                processing_time_ms=round(processing_time * 1000, 2),
                error=str(exc),
                error_type=type(exc).__name__,
                exc_info=True,
            )
            raise

        # Calculate processing time
        processing_time = time.time() - start_time

        # Log response
        logger.info(
            "Request completed",
            request_id=request_id,
            method=method,
            path=path,
            status_code=response.status_code,
            processing_time_ms=round(processing_time * 1000, 2),
        )

        # Add request ID to response headers
        response.headers["X-Request-ID"] = request_id

        return response


@asynccontextmanager
async def log_context(request: Request):
    """Context manager for adding request context to logs."""
    request_id = getattr(request.state, "request_id", None)
    if request_id:
        set_request_id(request_id)

    try:
        yield
    finally:
        pass
