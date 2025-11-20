"""Logging configuration."""

import logging
import logging.config
import sys
from typing import Any, Dict

import structlog
from pythonjsonlogger import jsonlogger


def configure_logging(log_level: str = "INFO", use_json: bool = False) -> None:
    """Configure structured logging."""
    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, log_level.upper()),
    )

    # Configure structlog processors
    processors = [
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
    ]

    if use_json:
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer(colors=True))

    # Configure structlog
    structlog.configure(
        processors=processors,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """Get a structured logger instance."""
    return structlog.get_logger(name)


def get_uvicorn_log_config(
    log_level: str = "info", use_json: bool = False
) -> Dict[str, Any]:
    """Get uvicorn logging configuration."""
    if use_json:
        formatter = {
            "()": jsonlogger.JsonFormatter,
            "format": "%(asctime)s %(name)s %(levelname)s %(message)s",
        }
    else:
        formatter = {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        }

    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": formatter,
        },
        "handlers": {
            "default": {
                "formatter": "default",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
            },
        },
        "root": {
            "level": log_level.upper(),
            "handlers": ["default"],
        },
        "loggers": {
            "uvicorn": {"level": log_level.upper(), "propagate": True},
            "uvicorn.error": {"level": log_level.upper(), "propagate": True},
            "uvicorn.access": {"level": log_level.upper(), "propagate": True},
        },
    }
