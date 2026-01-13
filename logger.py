"""Logging and Observability Module - CollectiveBrain Multi-Agent System

Centralized logging configuration with structured logging and metrics collection.
"""

import logging
import sys
from typing import Any, Dict
from datetime import datetime
import json


class StructuredFormatter(logging.Formatter):
    """Custom formatter for structured JSON logging."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Add extra fields
        if hasattr(record, "extra_fields"):
            log_data.update(record.extra_fields)

        return json.dumps(log_data)


class CollectiveBrainLogger:
    """Centralized logger for CollectiveBrain system."""

    def __init__(self, name: str = "collective_brain", level: str = "INFO"):
        """
        Initialize logger.

        Args:
            name: Logger name
            level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, level.upper()))

        # Remove existing handlers
        self.logger.handlers.clear()

        # Console handler with structured formatting
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(StructuredFormatter())
        self.logger.addHandler(console_handler)

    def debug(self, message: str, **extra: Any) -> None:
        """Log debug message."""
        self.logger.debug(message, extra={"extra_fields": extra})

    def info(self, message: str, **extra: Any) -> None:
        """Log info message."""
        self.logger.info(message, extra={"extra_fields": extra})

    def warning(self, message: str, **extra: Any) -> None:
        """Log warning message."""
        self.logger.warning(message, extra={"extra_fields": extra})

    def error(self, message: str, **extra: Any) -> None:
        """Log error message."""
        self.logger.error(message, extra={"extra_fields": extra})

    def critical(self, message: str, **extra: Any) -> None:
        """Log critical message."""
        self.logger.critical(message, extra={"extra_fields": extra})

    def log_event(self, event_type: str, event_data: Dict[str, Any]) -> None:
        """
        Log a structured event.

        Args:
            event_type: Type of event (task_created, consensus_reached, etc.)
            event_data: Event metadata
        """
        self.info(
            f"Event: {event_type}",
            event_type=event_type,
            **event_data
        )


class MetricsCollector:
    """Simple metrics collector for observability."""

    def __init__(self):
        """Initialize metrics collector."""
        self.metrics: Dict[str, Any] = {
            "objectives_processed": 0,
            "consensus_decisions": 0,
            "worker_tasks_completed": 0,
            "errors": 0,
            "start_time": datetime.utcnow().isoformat()
        }

    def increment(self, metric_name: str, value: int = 1) -> None:
        """Increment a metric counter."""
        if metric_name in self.metrics:
            self.metrics[metric_name] += value
        else:
            self.metrics[metric_name] = value

    def set(self, metric_name: str, value: Any) -> None:
        """Set a metric value."""
        self.metrics[metric_name] = value

    def get(self, metric_name: str) -> Any:
        """Get a metric value."""
        return self.metrics.get(metric_name)

    def get_all(self) -> Dict[str, Any]:
        """Get all metrics."""
        return {
            **self.metrics,
            "current_time": datetime.utcnow().isoformat()
        }

    def reset(self) -> None:
        """Reset all metrics."""
        self.metrics = {
            "objectives_processed": 0,
            "consensus_decisions": 0,
            "worker_tasks_completed": 0,
            "errors": 0,
            "start_time": datetime.utcnow().isoformat()
        }


# Global instances
_logger_instance = None
_metrics_instance = None


def get_logger(name: str = "collective_brain", level: str = "INFO") -> CollectiveBrainLogger:
    """Get or create global logger instance."""
    global _logger_instance
    if _logger_instance is None:
        _logger_instance = CollectiveBrainLogger(name, level)
    return _logger_instance


def get_metrics() -> MetricsCollector:
    """Get or create global metrics collector instance."""
    global _metrics_instance
    if _metrics_instance is None:
        _metrics_instance = MetricsCollector()
    return _metrics_instance


if __name__ == "__main__":
    # Example usage
    logger = get_logger(level="DEBUG")
    metrics = get_metrics()

    # Log some events
    logger.info("System initialized", component="orchestrator")
    logger.log_event("task_created", {
        "task_id": "task_123",
        "objective": "Test objective"
    })

    # Record metrics
    metrics.increment("objectives_processed")
    metrics.increment("worker_tasks_completed", 3)
    metrics.set("active_workers", 4)

    print("\nMetrics:")
    print(json.dumps(metrics.get_all(), indent=2))
