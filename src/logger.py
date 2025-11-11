"""Central logging utilities.

This module exposes helpers to configure logging for the application and to
retrieve loggers. It follows best-practices:

- does not configure global logging on import (call ``configure_logging`` at
  application startup)
- supports configuration via the ``LOG_LEVEL`` environment variable
- uses a clear ISO-like timestamp in log messages
- keeps existing loggers enabled (``disable_existing_loggers=False``)

Usage:
    from logger import configure_logging, get_logger
    configure_logging()  # once at startup
    logger = get_logger(__name__)
    logger.info("ready")
"""

from __future__ import annotations

import logging
import logging.config
import os
from typing import Optional

DEFAULT_LEVEL = "INFO"
DEFAULT_FORMAT = "%(asctime)s %(levelname)s %(name)s - %(message)s"
DEFAULT_DATEFMT = "%Y-%m-%dT%H:%M:%S%z"


def _resolve_level(level: Optional[str]) -> str:
    """Resolve a log level string or return the default.

    Accepts strings like 'INFO', 'debug', or numeric values as strings.
    Always returns an UPPERCASE name supported by logging.
    """
    if not level:
        return DEFAULT_LEVEL
    level = str(level).strip()
    # allow numeric levels provided as strings
    if level.isdigit():
        try:
            lvl = int(level)
            return logging.getLevelName(lvl)
        except Exception:
            return DEFAULT_LEVEL
    return level.upper()


def configure_logging(level: Optional[str] = None) -> None:
    """Configure root logging for the application.

    Parameters
    - level: optional level name or numeric string. If not provided the
      ``LOG_LEVEL`` environment variable is used, falling back to ``INFO``.

    This function uses ``logging.config.dictConfig`` to set a single
    console handler and a default formatter with an ISO-like timestamp.
    Call it once at application startup (for example in your FastAPI
    lifespan handler).
    """
    requested = level or os.getenv("LOG_LEVEL")
    level_name = _resolve_level(requested)

    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {"format": DEFAULT_FORMAT, "datefmt": DEFAULT_DATEFMT}
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "default",
                "level": level_name,
                "stream": "ext://sys.stdout",
            }
        },
        "root": {"handlers": ["console"], "level": level_name},
    }

    logging.config.dictConfig(config)


def get_logger(name: str = __name__) -> logging.Logger:
    """Return a logger for ``name``.

    This does not (re)configure logging by itself. Call ``configure_logging``
    early in your application to activate the console handler and desired
    level.
    """
    return logging.getLogger(name)


__all__ = ["configure_logging", "get_logger"]
