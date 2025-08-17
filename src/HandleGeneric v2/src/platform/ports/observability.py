"""Observability ports for logging, metrics, and tracing."""

from typing import Protocol, Dict, Any, Optional
import time
from contextlib import contextmanager


class Logger(Protocol):
    """Structured logging interface."""

    def debug(self, message: str, **kwargs: Any) -> None:
        """Log debug message."""
        ...

    def info(self, message: str, **kwargs: Any) -> None:
        """Log info message."""
        ...

    def warning(self, message: str, **kwargs: Any) -> None:
        """Log warning message."""
        ...

    def error(self, message: str, **kwargs: Any) -> None:
        """Log error message."""
        ...

    def critical(self, message: str, **kwargs: Any) -> None:
        """Log critical message."""
        ...


class Metrics(Protocol):
    """Metrics collection interface."""

    def counter(self, name: str, value: int = 1, tags: Optional[Dict[str, str]] = None) -> None:
        """Increment a counter."""
        ...

    def gauge(self, name: str, value: float, tags: Optional[Dict[str, str]] = None) -> None:
        """Set a gauge value."""
        ...

    def timer(self, name: str, value: float, tags: Optional[Dict[str, str]] = None) -> None:
        """Record a timing."""
        ...

    @contextmanager
    def time_context(self, name: str, tags: Optional[Dict[str, str]] = None):
        """Context manager for timing operations."""
        start = time.time()
        try:
            yield
        finally:
            duration = time.time() - start
            self.timer(name, duration, tags)


class Tracer(Protocol):
    """Distributed tracing interface."""

    def start_span(self, name: str, parent_id: Optional[str] = None) -> "Span":
        """Start a new span."""
        ...

    @contextmanager
    def trace(self, name: str, **kwargs: Any):
        """Context manager for tracing operations."""
        span = self.start_span(name)
        try:
            for key, value in kwargs.items():
                span.set_attribute(key, value)
            yield span
        finally:
            span.end()


class Span(Protocol):
    """Tracing span interface."""

    def set_attribute(self, key: str, value: Any) -> None:
        """Set an attribute on the span."""
        ...

    def add_event(self, name: str, attributes: Optional[Dict[str, Any]] = None) -> None:
        """Add an event to the span."""
        ...

    def end(self) -> None:
        """End the span."""
        ...
