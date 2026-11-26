"""Liveness endpoint. Must stay dependency-free and fast."""

from __future__ import annotations

from fastapi import APIRouter

from app.core.config import get_settings
from app.schemas.health import HealthResponse

router = APIRouter(tags=["health"])


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Liveness probe",
    description="Returns 200 once the process can serve HTTP. Does not touch the DB.",
)
async def health() -> HealthResponse:
    settings = get_settings()
    return HealthResponse(
        status="ok",
        version=settings.app_version,
        env=settings.app_env,
    )
