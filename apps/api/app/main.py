"""Application factory and process lifecycle.

Keep this file thin: it wires settings, middleware, exception handlers and
routers. Business logic belongs in services; HTTP mapping belongs in routes.
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import health
from app.core.config import Settings, get_settings
from app.core.errors import register_exception_handlers
from app.core.logging import configure_logging

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Startup/shutdown hooks.

    Heavy models are intentionally NOT loaded here; the first request that
    needs an embedding/reranker will load it (lazy loading, see LLMDOC).
    """
    settings: Settings = get_settings()
    logger.info(
        "api.start env=%s version=%s", settings.app_env, settings.app_version
    )
    yield
    logger.info("api.stop")


def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging("DEBUG" if settings.app_env == "development" else "INFO")

    expose_docs = settings.app_env != "production"
    app = FastAPI(
        title="TRACE // RAG Eval Workbench",
        version=settings.app_version,
        description="Knowledge chat + retrieval trace + evaluation workbench.",
        lifespan=lifespan,
        docs_url="/api/docs" if expose_docs else None,
        redoc_url=None,
        openapi_url="/api/openapi.json" if expose_docs else None,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    register_exception_handlers(app)
    app.include_router(health.router, prefix="/api")
    return app


app = create_app()
