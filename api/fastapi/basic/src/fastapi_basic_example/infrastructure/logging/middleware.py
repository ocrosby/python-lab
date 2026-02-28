"""Request logging middleware."""

from collections.abc import Callable
from contextlib import asynccontextmanager

import structlog
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from ..utils.id_generator import IdGenerator, UuidGenerator
from ..utils.time_provider import SystemTimeProvider, TimeProvider
from .context import set_request_id

logger = structlog.get_logger(__name__)


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Middleware for adding request ID to requests."""

    def __init__(
        self,
        app,
        id_generator: IdGenerator | None = None,
    ):
        super().__init__(app)
        self.id_generator = id_generator or UuidGenerator()

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Add request ID to request state and response headers."""
        request_id = self.id_generator.generate()
        set_request_id(request_id)
        request.state.request_id = request_id

        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id

        return response


class TimingMiddleware(BaseHTTPMiddleware):
    """Middleware for tracking request processing time."""

    def __init__(
        self,
        app,
        time_provider: TimeProvider | None = None,
    ):
        super().__init__(app)
        self.time_provider = time_provider or SystemTimeProvider()

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Track and log request processing time."""
        start_time = self.time_provider.time()

        response = await call_next(request)

        process_time = self.time_provider.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)

        request_id = getattr(request.state, "request_id", "unknown")
        logger.info(
            f"Request timing: {request.method} {request.url.path} - {process_time:.4f}s",
            request_id=request_id,
            method=request.method,
            path=request.url.path,
            process_time=process_time,
        )

        return response


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging HTTP requests and responses."""

    def __init__(self, app):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process the request and log details."""
        request_id = getattr(request.state, "request_id", "unknown")
        method = request.method
        url = str(request.url)
        path = request.url.path
        query_params = dict(request.query_params)
        client_ip = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")

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
            response = await call_next(request)
        except Exception as exc:
            logger.error(
                "Request failed",
                request_id=request_id,
                method=method,
                path=path,
                error=str(exc),
                error_type=type(exc).__name__,
                exc_info=True,
            )
            raise

        logger.info(
            "Request completed",
            request_id=request_id,
            method=method,
            path=path,
            status_code=response.status_code,
        )

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
