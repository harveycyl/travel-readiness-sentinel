"""
Logging configuration for Travel Readiness Sentinel API.
Provides structured JSON logging for production observability.
"""
import logging
import sys
from pythonjsonlogger import jsonlogger
from typing import Optional
import uuid
from contextvars import ContextVar

# Context variable for request ID tracking
request_id_var: ContextVar[Optional[str]] = ContextVar('request_id', default=None)


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """
    Custom JSON formatter that includes request ID and additional context.
    """
    def add_fields(self, log_record, record, message_dict):
        super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)
        
        # Add timestamp
        if not log_record.get('timestamp'):
            log_record['timestamp'] = self.formatTime(record, self.datefmt)
        
        # Add log level
        if log_record.get('level'):
            log_record['level'] = log_record['level'].upper()
        else:
            log_record['level'] = record.levelname
        
        # Add request ID if available
        request_id = request_id_var.get()
        if request_id:
            log_record['request_id'] = request_id


def setup_logging(log_level: str = "INFO", log_format: str = "json") -> logging.Logger:
    """
    Configure application logging.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_format: Format type ('json' or 'text')
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger("trs")
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Remove existing handlers
    logger.handlers = []
    
    # Create console handler
    handler = logging.StreamHandler(sys.stdout)
    
    if log_format.lower() == "json":
        # JSON formatter for production
        formatter = CustomJsonFormatter(
            '%(timestamp)s %(level)s %(name)s %(message)s',
            datefmt='%Y-%m-%dT%H:%M:%S'
        )
    else:
        # Simple text formatter for development
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    return logger


def set_request_id(request_id: str = None) -> str:
    """
    Set request ID for current context.
    
    Args:
        request_id: Optional request ID. If not provided, generates a new UUID.
    
    Returns:
        The request ID that was set
    """
    if request_id is None:
        request_id = str(uuid.uuid4())
    
    request_id_var.set(request_id)
    return request_id


def get_request_id() -> Optional[str]:
    """
    Get current request ID from context.
    
    Returns:
        Current request ID or None if not set
    """
    return request_id_var.get()


def clear_request_id():
    """Clear request ID from current context."""
    request_id_var.set(None)


# Create default logger instance
logger = setup_logging()
