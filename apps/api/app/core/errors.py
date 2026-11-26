"""One error envelope for every failure the API can return.

Frontend contract (docs/API.md):
    {"error": {"code": "NOT_FOUND", "message": "...", "details": ...}}

Routes raise AppError for expected failures; framework exceptions are mapped
here so clients never have to parse FastAPI's default {"detail": ...} shape.
"""

from __future__ import annotations

import logging
from typing import Any

from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger(__name__)


class AppError(Exception):
    """Expected, domain-level failure with a stable machine-readable code."""

    def __init__(
        self,
        code: str,
        message: str,
        *,
        status_code: int = 400,
        details: Any = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details


def error_response(
    status_code: int,
    code: str,
    message: str,
    details: Any = None,
) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={"error": {"code": code, "message": message, "details": details}},
    )


async def app_error_handler(_: Request, exc: AppError) -> JSONResponse:
    return error_response(exc.status_code, exc.code, exc.message, exc.details)


async def http_error_handler(_: Request, exc: StarletteHTTPException) -> JSONResponse:
    """Map Starlette/FastAPI HTTPException to the same envelope."""
    default_codes = {404: "NOT_FOUND", 405: "METHOD_NOT_ALLOWED", 401: "UNAUTHORIZED"}
    code = default_codes.get(exc.status_code, "HTTP_ERROR")
    detail = exc.detail
    message = detail if isinstance(detail, str) else "Request failed"
    details = None if isinstance(detail, str) else detail
    return error_response(exc.status_code, code, message, details)


async def validation_error_handler(
    _: Request, exc: RequestValidationError
) -> JSONResponse:
    return error_response(
        422,
        "VALIDATION_ERROR",
        "Request validation failed",
        jsonable_encoder(exc.errors()),
    )


async def unhandled_error_handler(request: Request, exc: Exception) -> JSONResponse:
    """Last resort: log the stack, return no internal details to the client."""
    logger.exception("Unhandled error on %s %s", request.method, request.url.path)
    return error_response(500, "INTERNAL_ERROR", "Internal server error")


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(AppError, app_error_handler)
    app.add_exception_handler(StarletteHTTPException, http_error_handler)
    app.add_exception_handler(RequestValidationError, validation_error_handler)
    app.add_exception_handler(Exception, unhandled_error_handler)
