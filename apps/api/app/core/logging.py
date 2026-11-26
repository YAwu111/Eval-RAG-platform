"""Minimal logging setup shared by the API process."""

from __future__ import annotations

import logging
import sys

_FORMAT = "%(asctime)s %(levelname)-7s %(name)s | %(message)s"


def configure_logging(level: str = "INFO") -> None:
    """Configure the root logger once, writing to stdout (container-friendly)."""
    logging.basicConfig(
        level=level.upper(),
        format=_FORMAT,
        datefmt="%H:%M:%S",
        stream=sys.stdout,
        force=True,
    )
