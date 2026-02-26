"""Logging decorator for cross-cutting concerns."""

import functools
import inspect
from collections.abc import Callable
from typing import TypeVar

import structlog

from ..logging.context import get_logger_context

F = TypeVar("F", bound=Callable)


def log_execution(logger_name: str) -> Callable:
    """Decorator to log function execution.

    Args:
        logger_name: Name of the logger to use

    Returns:
        Decorated function with automatic logging

    Example:
        @log_execution("use_cases")
        async def my_use_case(self, param: int) -> Result:
            return await self._do_work(param)
    """

    def decorator(func: F) -> F:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            logger = structlog.get_logger(logger_name)
            func_name = func.__name__

            logger.info(f"Executing {func_name}", **get_logger_context())
            try:
                result = await func(*args, **kwargs)
                logger.info(f"Completed {func_name}", **get_logger_context())
                return result
            except Exception as e:
                logger.error(
                    f"Failed {func_name}",
                    error=str(e),
                    error_type=type(e).__name__,
                    **get_logger_context(),
                )
                raise

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            logger = structlog.get_logger(logger_name)
            func_name = func.__name__

            logger.info(f"Executing {func_name}", **get_logger_context())
            try:
                result = func(*args, **kwargs)
                logger.info(f"Completed {func_name}", **get_logger_context())
                return result
            except Exception as e:
                logger.error(
                    f"Failed {func_name}",
                    error=str(e),
                    error_type=type(e).__name__,
                    **get_logger_context(),
                )
                raise

        if inspect.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper

    return decorator
