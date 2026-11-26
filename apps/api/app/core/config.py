"""Typed application settings loaded from the repository-root .env file.

One Settings object is created per process (cached), so importing this module
never reads secrets twice. Routes/services receive settings via dependency
injection instead of importing a global.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Annotated, Literal

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict

# apps/api/app/core/config.py -> repository root
REPO_ROOT = Path(__file__).resolve().parents[4]


class Settings(BaseSettings):
    """Environment-backed configuration.

    Field names are lower-case; pydantic-settings matches them to upper-case
    environment variables (DATABASE_URL -> database_url) case-insensitively.
    """

    model_config = SettingsConfigDict(
        env_file=REPO_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    app_env: Literal["development", "test", "production"] = "development"
    app_version: str = "0.1.0"
    api_host: str = "127.0.0.1"
    api_port: int = 8000
    # NoDecode: keep the raw string so the validator below can split on commas
    # instead of pydantic-settings trying to JSON-decode it first.
    cors_origins: Annotated[list[str], NoDecode] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

    database_url: str = (
        "postgresql+psycopg://rag_eval:rag_eval_dev@localhost:5433/rag_eval"
    )
    upload_dir: str = "./data/uploads"
    max_upload_mb: int = 20

    @field_validator("cors_origins", mode="before")
    @classmethod
    def split_origins(cls, value: object) -> object:
        """Accept a JSON array or a comma-separated string.

        pydantic-settings JSON-decodes list fields by default; NoDecode keeps
        the raw value so both .env styles work.
        """
        if not isinstance(value, str):
            return value
        text = value.strip()
        if text.startswith("["):
            return json.loads(text)
        return [item.strip() for item in text.split(",") if item.strip()]

    @model_validator(mode="after")
    def reject_dev_secrets_in_production(self) -> "Settings":
        """Fail fast instead of booting production with the local dev DB."""
        if self.app_env == "production" and "rag_eval_dev" in self.database_url:
            raise ValueError(
                "DATABASE_URL still uses the local dev password; set a real one"
            )
        return self


@lru_cache
def get_settings() -> Settings:
    """Return the process-wide Settings singleton."""
    return Settings()
