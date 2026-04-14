import logging
import sys
from typing import Optional
from src.core.config import settings


def setup_logging():
    """Configure logging for the application."""
    level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)

    # Get the root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Remove existing handlers
    for handler in list(root_logger.handlers):
        root_logger.removeHandler(handler)

    # Create our handler
    handler = logging.StreamHandler(sys.stderr)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    root_logger.addHandler(handler)

    # Also explicitly configure some common libraries
    for logger_name in ["fastmcp", "mcp", "uvicorn"]:
        lib_logger = logging.getLogger(logger_name)
        lib_logger.setLevel(level)
        lib_logger.propagate = True


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Get a logger instance."""
    prefix = "tutto-mcp-server"
    if name:
        return logging.getLogger(f"{prefix}.{name}")
    return logging.getLogger(prefix)
