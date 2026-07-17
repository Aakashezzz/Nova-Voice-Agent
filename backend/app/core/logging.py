"""
Structured logging setup.

A single call to `configure_logging()` at process startup gives every
module a consistently formatted logger via `logging.getLogger(__name__)`.
"""
import logging
import sys

from app.core.config import get_settings


def configure_logging() -> None:
    """Configure root logging handlers and formatting. Call once at startup."""
    settings = get_settings()

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(settings.log_level)
    # Avoid duplicate handlers on reload
    root_logger.handlers.clear()
    root_logger.addHandler(handler)

    # Quiet down noisy third-party loggers
    for noisy in ("uvicorn.access", "httpx", "faster_whisper"):
        logging.getLogger(noisy).setLevel(logging.WARNING)
