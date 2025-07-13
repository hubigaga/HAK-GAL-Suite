"""
HAK-GAL Structured Logging Configuration
========================================

Integrates HAK-GAL Backend with Grafana Loki for centralized logging.
Provides structured JSON logging with trace correlation and performance metrics.

Usage:
    from backend.logging_config import setup_hak_gal_logging
    setup_hak_gal_logging()
"""

import logging
import logging.handlers
import json
import time
import traceback
import sys
import os
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path
import uuid

# Create logs directory
LOGS_DIR = Path("observability/logs")
LOGS_DIR.mkdir(parents=True, exist_ok=True)


class HAKGALJsonFormatter(logging.Formatter):
    """
    Custom JSON formatter for HAK-GAL logs
    Optimized for Loki parsing and Grafana visualization
    """

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as structured JSON"""
        
        # Base log structure
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "service": "hak-gal-backend",
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "message": record.getMessage(),
            "logger": record.name,
            "thread": record.thread,
            "process": record.process
        }

        # Add HAK-GAL specific fields
        if hasattr(record, 'trace_id'):
            log_entry['trace_id'] = record.trace_id
            
        if hasattr(record, 'span_id'):
            log_entry['span_id'] = record.span_id
            
        if hasattr(record, 'user_id'):
            log_entry['user_id'] = record.user_id
            
        if hasattr(record, 'command'):
            log_entry['command'] = record.command
            
        if hasattr(record, 'query_time_ms'):
            log_entry['query_time_ms'] = record.query_time_ms
            
        if hasattr(record, 'backend_issue'):
            log_entry['backend_issue'] = record.backend_issue
            
        if hasattr(record, 'error_type'):
            log_entry['error_type'] = record.error_type
            
        if hasattr(record, 'operation'):
            log_entry['operation'] = record.operation
            
        if hasattr(record, 'memory_mb'):
            log_entry['memory_mb'] = record.memory_mb
            
        if hasattr(record, 'cpu_percent'):
            log_entry['cpu_percent'] = record.cpu_percent

        # Add exception information
        if record.exc_info:
            log_entry['exception'] = {
                'type': record.exc_info[0].__name__ if record.exc_info[0] else None,
                'message': str(record.exc_info[1]) if record.exc_info[1] else None,
                'traceback': self.formatException(record.exc_info)
            }

        # Add extra fields from LoggerAdapter
        if hasattr(record, 'extra_data'):
            log_entry.update(record.extra_data)

        return json.dumps(log_entry, ensure_ascii=False)


class HAKGALLoggerAdapter(logging.LoggerAdapter):
    """
    Logger adapter for HAK-GAL with automatic trace correlation
    """

    def __init__(self, logger: logging.Logger, extra: Dict[str, Any] = None):
        super().__init__(logger, extra or {})
        self.trace_id = str(uuid.uuid4())[:8]  # Short trace ID

    def process(self, msg: str, kwargs: Dict[str, Any]) -> tuple:
        """Add trace context to log records"""
        if 'extra' not in kwargs:
            kwargs['extra'] = {}
            
        # Add trace context
        kwargs['extra']['trace_id'] = self.trace_id
        
        # Add any additional context
        kwargs['extra'].update(self.extra)
        
        return msg, kwargs

    def log_performance(self, operation: str, duration_ms: float, 
                       memory_mb: float = None, cpu_percent: float = None,
                       **kwargs):
        """Log performance metrics"""
        extra = {
            'operation': operation,
            'query_time_ms': duration_ms,
            'performance_log': True
        }
        
        if memory_mb:
            extra['memory_mb'] = memory_mb
        if cpu_percent:
            extra['cpu_percent'] = cpu_percent
            
        extra.update(kwargs)
        
        self.info(f"Performance: {operation} completed in {duration_ms:.2f}ms", 
                 extra=extra)

    def log_backend_issue(self, issue_id: str, error_message: str, 
                         error_type: str = None, **kwargs):
        """Log HAK-GAL backend issues with Sentry correlation"""
        extra = {
            'backend_issue': issue_id,
            'error_type': error_type or 'unknown',
            'sentry_issue': True
        }
        extra.update(kwargs)
        
        self.error(f"BACKEND-{issue_id}: {error_message}", extra=extra)

    def log_command(self, command: str, user_id: str = None, 
                   query_time_ms: float = None, **kwargs):
        """Log HAK-GAL command execution"""
        extra = {
            'command': command,
            'command_log': True
        }
        
        if user_id:
            extra['user_id'] = user_id
        if query_time_ms:
            extra['query_time_ms'] = query_time_ms
            
        extra.update(kwargs)
        
        self.info(f"Command executed: {command}", extra=extra)


def setup_hak_gal_logging(log_level: str = "INFO", 
                         enable_loki: bool = True,
                         enable_file: bool = True,
                         enable_console: bool = True) -> HAKGALLoggerAdapter:
    """
    Setup structured logging for HAK-GAL Backend
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        enable_loki: Enable Loki-compatible file logging
        enable_file: Enable separate file logging
        enable_console: Enable console logging
        
    Returns:
        Configured HAKGALLoggerAdapter
    """
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # JSON Formatter for structured logging
    json_formatter = HAKGALJsonFormatter()
    
    # Console Handler (if enabled)
    if enable_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(module)s.%(funcName)s:%(lineno)d | %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        root_logger.addHandler(console_handler)

    # File Handler for general logs
    if enable_file:
        file_handler = logging.handlers.RotatingFileHandler(
            LOGS_DIR / "api.log",
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(json_formatter)
        root_logger.addHandler(file_handler)

    # Loki-compatible handler
    if enable_loki:
        loki_handler = logging.handlers.RotatingFileHandler(
            LOGS_DIR / "hak-gal-loki.log",
            maxBytes=50 * 1024 * 1024,  # 50MB for Loki
            backupCount=3
        )
        loki_handler.setLevel(logging.DEBUG)
        loki_handler.setFormatter(json_formatter)
        root_logger.addHandler(loki_handler)

    # Separate handlers for specific log types
    
    # Performance logs
    perf_handler = logging.handlers.RotatingFileHandler(
        LOGS_DIR / "performance.log",
        maxBytes=20 * 1024 * 1024,
        backupCount=3
    )
    perf_handler.setLevel(logging.INFO)
    perf_handler.setFormatter(json_formatter)
    
    # Sentry correlation logs
    sentry_handler = logging.handlers.RotatingFileHandler(
        LOGS_DIR / "sentry.log",
        maxBytes=10 * 1024 * 1024,
        backupCount=5
    )
    sentry_handler.setLevel(logging.ERROR)
    sentry_handler.setFormatter(json_formatter)
    
    # Advanced tools logs
    tools_handler = logging.handlers.RotatingFileHandler(
        LOGS_DIR / "advanced_tools.log",
        maxBytes=15 * 1024 * 1024,
        backupCount=3
    )
    tools_handler.setLevel(logging.DEBUG)
    tools_handler.setFormatter(json_formatter)

    # Configure specific loggers
    perf_logger = logging.getLogger('hak_gal.performance')
    perf_logger.addHandler(perf_handler)
    perf_logger.propagate = False
    
    sentry_logger = logging.getLogger('hak_gal.sentry')
    sentry_logger.addHandler(sentry_handler)
    sentry_logger.propagate = False
    
    tools_logger = logging.getLogger('hak_gal.tools')
    tools_logger.addHandler(tools_handler)
    tools_logger.propagate = False

    # Create HAK-GAL adapter
    hak_gal_logger = logging.getLogger('hak_gal.main')
    adapter = HAKGALLoggerAdapter(hak_gal_logger, {'component': 'backend'})
    
    # Log initialization
    adapter.info("HAK-GAL structured logging initialized", 
                extra={
                    'log_level': log_level,
                    'loki_enabled': enable_loki,
                    'handlers_count': len(root_logger.handlers),
                    'logs_directory': str(LOGS_DIR.absolute())
                })
    
    return adapter


def get_hak_gal_logger(component: str = "backend") -> HAKGALLoggerAdapter:
    """Get a HAK-GAL logger adapter for a specific component"""
    logger = logging.getLogger(f'hak_gal.{component}')
    return HAKGALLoggerAdapter(logger, {'component': component})


# Context manager for performance logging
class LogPerformance:
    """Context manager for automatic performance logging"""
    
    def __init__(self, logger: HAKGALLoggerAdapter, operation: str, **kwargs):
        self.logger = logger
        self.operation = operation
        self.extra = kwargs
        self.start_time = None

    def __enter__(self):
        self.start_time = time.time()
        self.logger.debug(f"Starting operation: {self.operation}", 
                         extra={'operation_start': True, **self.extra})
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        duration_ms = (time.time() - self.start_time) * 1000
        
        if exc_type:
            self.logger.log_backend_issue(
                "PERFORMANCE", 
                f"Operation {self.operation} failed after {duration_ms:.2f}ms",
                error_type="performance_failure",
                operation=self.operation,
                query_time_ms=duration_ms,
                exception_type=exc_type.__name__,
                **self.extra
            )
        else:
            self.logger.log_performance(
                self.operation, 
                duration_ms, 
                **self.extra
            )


# Example usage and testing
if __name__ == "__main__":
    # Setup logging
    logger = setup_hak_gal_logging(log_level="DEBUG")
    
    # Test different log types
    logger.info("HAK-GAL backend started")
    
    # Test command logging
    logger.log_command("explain machine learning", user_id="test_user", query_time_ms=1250.5)
    
    # Test performance logging
    logger.log_performance("relevance_query", 850.2, memory_mb=25.4, cpu_percent=45.2)
    
    # Test backend issue logging
    logger.log_backend_issue("7", "asyncio Future detection failed", 
                           error_type="asyncio", command="learn_facts")
    
    # Test context manager
    with LogPerformance(logger, "complex_query", user_id="test", command="ask"):
        time.sleep(0.1)  # Simulate work
        logger.info("Processing complex query")
    
    # Test exception logging
    try:
        raise ValueError("Test exception for logging")
    except Exception as e:
        logger.error("Exception occurred during processing", exc_info=True,
                    extra={'error_type': 'test_error', 'operation': 'testing'})
    
    print("✅ HAK-GAL logging test completed. Check logs in observability/logs/")
