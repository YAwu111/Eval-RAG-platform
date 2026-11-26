"""Schemas shared by more than one route."""

from __future__ import annotations

from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class ErrorDetail(BaseModel):
    code: str = Field(examples=["NOT_FOUND"])
    message: str
    details: Any | None = None


class ErrorResponse(BaseModel):
    error: ErrorDetail


class Page(BaseModel, Generic[T]):
    """Offset pagination envelope used by list endpoints."""

    items: list[T]
    total: int
    limit: int
    offset: int
