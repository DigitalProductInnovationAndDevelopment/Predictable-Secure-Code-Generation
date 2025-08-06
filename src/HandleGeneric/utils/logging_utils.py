"""
Logging utility functions for HandleGeneric.

This module contains utility functions for logging configuration.
"""

import logging
import sys
from pathlib import Path
from typing import Optional, Dict, Any


def setup_logging(
    level: str = "INFO",
    log_file: Optional[Path] = None,
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    date_format: str = "%Y-%m-%d %H:%M:%S",
    verbose: bool = False,
) -> None:
    """
    Setup logging configuration.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional file path for logging
        log_format: Format string for log messages
        date_format: Format string for timestamps
        verbose: If True, sets level to DEBUG
    """
    # Convert string level to logging constant
    level_map = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL,
    }

    log_level = level_map.get(level.upper(), logging.INFO)
    if verbose:
        log_level = logging.DEBUG

    # Create formatter
    formatter = logging.Formatter(log_format, date_format)

    # Setup root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Clear existing handlers
    root_logger.handlers.clear()

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # File handler (if specified)
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance.

    Args:
        name: Logger name

    Returns:
        Logger instance
    """
    return logging.getLogger(name)


def log_function_call(
    logger: logging.Logger, func_name: str, args: Dict[str, Any] = None
) -> None:
    """
    Log a function call with its arguments.

    Args:
        logger: Logger instance
        func_name: Name of the function being called
        args: Function arguments (optional)
    """
    if args:
        logger.debug(f"Calling {func_name} with args: {args}")
    else:
        logger.debug(f"Calling {func_name}")


def log_function_result(
    logger: logging.Logger, func_name: str, result: Any = None, error: Exception = None
) -> None:
    """
    Log a function result or error.

    Args:
        logger: Logger instance
        func_name: Name of the function
        result: Function result (optional)
        error: Exception if function failed (optional)
    """
    if error:
        logger.error(f"{func_name} failed: {error}")
    else:
        logger.debug(f"{func_name} completed successfully")
        if result is not None:
            logger.debug(f"{func_name} returned: {result}")


def create_logger_with_context(name: str, context: Dict[str, Any]) -> logging.Logger:
    """
    Create a logger with context information.

    Args:
        name: Logger name
        context: Context information to include in log messages

    Returns:
        Logger with context
    """
    logger = logging.getLogger(name)

    # Create a custom formatter that includes context
    class ContextFormatter(logging.Formatter):
        def format(self, record):
            # Add context to the record
            for key, value in context.items():
                setattr(record, key, value)

            # Update the format to include context
            if hasattr(record, "context"):
                record.msg = f"[{record.context}] {record.msg}"

            return super().format(record)

    # Apply the formatter to all handlers
    for handler in logger.handlers:
        handler.setFormatter(ContextFormatter())

    return logger
