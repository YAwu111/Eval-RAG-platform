"""Settings parsing edge cases that bit us in review."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.core.config import Settings


def test_cors_accepts_comma_separated_string() -> None:
    settings = Settings(cors_origins="http://a.test, http://b.test")

    assert settings.cors_origins == ["http://a.test", "http://b.test"]


def test_cors_accepts_json_array_string() -> None:
    settings = Settings(cors_origins='["http://a.test", "http://b.test"]')

    assert settings.cors_origins == ["http://a.test", "http://b.test"]


def test_production_rejects_dev_database_password() -> None:
    with pytest.raises(ValidationError, match="local dev password"):
        Settings(
            app_env="production",
            database_url=(
                "postgresql+psycopg://rag_eval:rag_eval_dev@localhost:5433/rag_eval"
            ),
        )
