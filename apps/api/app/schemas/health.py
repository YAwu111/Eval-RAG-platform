"""Health/readiness response models."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

HealthStatus = Literal["ok", "degraded", "down"]
ModelStatus = Literal["lazy", "ready", "failed"]


class HealthResponse(BaseModel):
    """Liveness payload; db is "unknown" until the DB is wired in M1-2."""

    status: HealthStatus = "ok"
    version: str
    db: Literal["ok", "unknown", "down"] = "unknown"
    models: dict[str, ModelStatus] = Field(
        default_factory=lambda: {
            "embedding": "lazy",
            "reranker": "lazy",
            "judges": "lazy",
        }
    )
