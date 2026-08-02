"""Structlog configuration shared by Django's logging and application code.

Every log line — whether emitted by Django, aiogram, or our own
`structlog.get_logger(...)` calls — is rendered by the same formatter,
so logs are uniformly structured (JSON in production, readable console
output in development).
"""

from __future__ import annotations

import structlog

_SHARED_PROCESSORS = [
    structlog.contextvars.merge_contextvars,
    structlog.stdlib.add_log_level,
    structlog.stdlib.add_logger_name,
    structlog.processors.TimeStamper(fmt="iso"),
    structlog.processors.StackInfoRenderer(),
    structlog.processors.format_exc_info,
]


def configure_structlog() -> None:
    """Configure structlog's processor chain. Call once, at settings import time."""
    structlog.configure(
        processors=_SHARED_PROCESSORS + [structlog.stdlib.ProcessorFormatter.wrap_for_formatter],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


def build_logging_config(*, log_level: str, json_logs: bool) -> dict:
    """Build Django's LOGGING dict, rendering every log line through structlog."""
    renderer = (
        structlog.processors.JSONRenderer()
        if json_logs
        else structlog.dev.ConsoleRenderer(colors=True)
    )

    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "structlog": {
                "()": structlog.stdlib.ProcessorFormatter,
                "processors": [
                    structlog.stdlib.ProcessorFormatter.remove_processors_meta,
                    renderer,
                ],
                "foreign_pre_chain": _SHARED_PROCESSORS,
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "structlog",
            },
        },
        "root": {
            "handlers": ["console"],
            "level": log_level,
        },
        "loggers": {
            "django": {
                "handlers": ["console"],
                "level": log_level,
                "propagate": False,
            },
            "aiogram": {
                "handlers": ["console"],
                "level": log_level,
                "propagate": False,
            },
            "bizynex": {
                "handlers": ["console"],
                "level": log_level,
                "propagate": False,
            },
        },
    }
