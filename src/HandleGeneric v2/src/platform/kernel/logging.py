"""Structured logging configuration."""

import logging
import sys
from typing import Any

# Try to import structlog, fall back to standard logging if not available
try:
    import structlog

    HAS_STRUCTLOG = True
except ImportError:
    HAS_STRUCTLOG = False


class LoggerWrapper:
    """Wrapper to handle differences between structlog and standard logging."""

    def __init__(self, logger):
        self.logger = logger
        self.is_structlog = HAS_STRUCTLOG and hasattr(logger, "bind")

    def _format_message(self, message: str, **kwargs) -> str:
        """Format message with context for standard logging."""
        if not kwargs:
            return message

        context_parts = []
        for key, value in kwargs.items():
            # Avoid 'file' and 'message' keywords which conflict with logging
            if key == "file":
                key = "filepath"
            elif key == "message":
                key = "msg"
            context_parts.append(f"{key}={value}")

        return f"{message} [{', '.join(context_parts)}]"

    def debug(self, message: str, **kwargs):
        if self.is_structlog:
            self.logger.debug(message, **kwargs)
        else:
            self.logger.debug(self._format_message(message, **kwargs))

    def info(self, message: str, **kwargs):
        if self.is_structlog:
            self.logger.info(message, **kwargs)
        else:
            self.logger.info(self._format_message(message, **kwargs))

    def warning(self, message: str, **kwargs):
        if self.is_structlog:
            self.logger.warning(message, **kwargs)
        else:
            self.logger.warning(self._format_message(message, **kwargs))

    def error(self, message: str, **kwargs):
        if self.is_structlog:
            self.logger.error(message, **kwargs)
        else:
            self.logger.error(self._format_message(message, **kwargs))

    def critical(self, message: str, **kwargs):
        if self.is_structlog:
            self.logger.critical(message, **kwargs)
        else:
            self.logger.critical(self._format_message(message, **kwargs))


def setup_logging(level: str = "INFO", format_type: str = "json") -> None:
    """Setup structured logging with structlog or fallback to standard logging."""

    # Configure standard library logging
    if format_type == "json" and HAS_STRUCTLOG:
        log_format = "%(message)s"
    else:
        log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    logging.basicConfig(
        format=log_format,
        stream=sys.stdout,
        level=getattr(logging, level.upper()),
    )

    if HAS_STRUCTLOG:
        # Configure structlog processors
        processors = [
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
        ]

        if format_type == "json":
            processors.append(structlog.processors.JSONRenderer())
        else:
            processors.extend(
                [
                    structlog.dev.ConsoleRenderer(colors=True),
                ]
            )

        structlog.configure(
            processors=processors,
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )


def get_logger(name: str) -> LoggerWrapper:
    """Get a structured logger."""
    if HAS_STRUCTLOG:
        return LoggerWrapper(structlog.get_logger(name))
    else:
        return LoggerWrapper(logging.getLogger(name))
