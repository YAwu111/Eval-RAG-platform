"""One error envelope for every failure the API can return.

Frontend contract (docs/API.md):
    {"error": {"code": "NOT_FOUND", "message": "...", "details": ...}}

Routes raise AppError for expected failures; framework exceptions are mapped
here so clients never have to parse FastAPI's default {"detail": ...} shape.
"""

from __future__ import annotations

import logging
from collections.abc import Mapping
from typing import Any

from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.config import get_settings

logger = logging.getLogger(__name__)

# HTTP status -> stable machine code used by the frontend.
_STATUS_CODES = {
    400: "BAD_REQUEST",
    401: "UNAUTHORIZED",
    403: "FORBIDDEN",
    404: "NOT_FOUND",
    405: "METHOD_NOT_ALLOWED",
    409: "CONFLICT",
    413: "PAYLOAD_TOO_LARGE",
    415: "UNSUPPORTED_MEDIA_TYPE",
    429: "RATE_LIMITED",
    503: "SERVICE_UNAVAILABLE",
}


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


def _cors_headers(request: Request) -> dict[str, str] | None:
    """CORS headers for responses produced outside CORSMiddleware.

    Starlette's ServerErrorMiddleware wraps the whole app, so a 500 escapes the
    inner CORS middleware. Browsers would see a network error instead of the
    JSON envelope; add the header here for allowed origins.
    """
    origin = request.headers.get("origin")
    if origin and origin in get_settings().cors_origins:
        return {"access-control-allow-origin": origin, "vary": "Origin"}
    return None


def error_response(
    status_code: int,
    code: str,
    message: str,
    details: Any = None,
    *,
    headers: Mapping[str, str] | None = None,
) -> JSONResponse:
    # jsonable_encoder keeps datetime/UUID/Decimal details serializable; passing
    # them straight to JSONResponse would fail inside the error handler itself.
    content = jsonable_encoder(
        {"error": {"code": code, "message": message, "details": details}}
    )
    return JSONResponse(status_code=status_code, content=content, headers=headers)


async def app_error_handler(_: Request, exc: AppError) -> JSONResponse:
    return error_response(exc.status_code, exc.code, exc.message, exc.details)


async def http_error_handler(_: Request, exc: StarletteHTTPException) -> JSONResponse:
    """Map Starlette/FastAPI HTTPException to the same envelope."""
    code = _STATUS_CODES.get(exc.status_code, "HTTP_ERROR")
    detail = exc.detail
    message = detail if isinstance(detail, str) else "Request failed"
    details = None if isinstance(detail, str) else detail
    return error_response(
        exc.status_code,
        code,
        message,
        details,
        headers=exc.headers,
    )


async def validation_error_handler(
    _: Request, exc: RequestValidationError
) -> JSONResponse:
    # Do not echo pydantic's "input": it can contain passwords, tokens or file
    # bytes. type/loc/msg is enough for a client to fix the request.
    details = [
        {"type": item.get("type"), "loc": list(item.get("loc", [])), "msg": item.get("msg")}
        for item in exc.errors()
    ]
    return error_response(422, "VALIDATION_ERROR", "Request validation failed", details)


async def unhandled_error_handler(request: Request, exc: Exception) -> JSONResponse:
    """Last resort: return no internal details to the client."""
    # ServerErrorMiddleware/uvicorn already logs the traceback; logging here
    # with logger.exception would print it twice.
    logger.error("Unhandled error on %s %s", request.method, request.url.path)
    return error_response(
        500,
        "INTERNAL_ERROR",
        "Internal server error",
        headers=_cors_headers(request),
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(AppError, app_error_handler)
    app.add_exception_handler(StarletteHTTPException, http_error_handler)
    app.add_exception_handler(RequestValidationError, validation_error_handler)
    app.add_exception_handler(Exception, unhandled_error_handler)
