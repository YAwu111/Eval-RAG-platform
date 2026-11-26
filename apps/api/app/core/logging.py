"""Minimal logging setup shared by the API process."""

from __future__ import annotations

import logging
import sys

_FORMAT = "%(asctime)s %(levelname)-7s %(name)s | %(message)s"


def configure_logging(level: str = "INFO") -> None:
    """Configure logging only when nobody else has.

    Uvicorn and pytest install their own handlers; force=True would wipe them
    (and caplog). The application should add a fallback, not take over.
    """
    if logging.getLogger().handlers:
        return
    logging.basicConfig(
        level=level.upper(),
        format=_FORMAT,
        datefmt="%H:%M:%S",
        stream=sys.stdout,
    )
