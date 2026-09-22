"""
app/core/config.py
──────────────────
Application-wide settings loaded from environment variables using pydantic-settings.
All configuration values are typed and validated at startup.

Imported throughout the backend as:
    from app.core.config import settings
"""

from __future__ import annotations

from functools import lru_cache
from typing import List

from pydantic import AnyHttpUrl, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Central settings class.
    Values are read from the .env file (or environment variables).
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── MongoDB Atlas ──────────────────────────────────────────────────────
    MONGODB_URL: str = Field(
        default="mongodb://localhost:27017",
        description="Full MongoDB Atlas connection string.",
    )
    DATABASE_NAME: str = Field(
        default="medical_report_analyzer",
        description="MongoDB database name.",
    )

    # ── JWT Authentication ─────────────────────────────────────────────────
    SECRET_KEY: str = Field(
        default="changeme-insecure-default",
        description="Secret key for JWT signing. Must be changed in production.",
    )
    ALGORITHM: str = Field(default="HS256", description="JWT signing algorithm.")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=30, description="JWT access token lifetime in minutes."
    )

    # ── Ollama AI ───────────────────────────────────────────────────────────
    OLLAMA_BASE_URL: str = Field(
        default="http://localhost:11434", description="Base URL for local Ollama instance."
    )
    OLLAMA_MODEL: str = Field(
        default="llama3", description="Ollama model to use for analysis."
    )

    # ── CORS ───────────────────────────────────────────────────────────────
    ALLOWED_ORIGINS: str | List[str] = Field(
        default=["http://localhost:5173"],
        description="List of allowed CORS origins.",
    )

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def parse_allowed_origins(cls, v: object) -> List[str]:
        """Support comma-separated string OR a Python list from the env file."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v  # type: ignore[return-value]

    # ── File Uploads ───────────────────────────────────────────────────────
    UPLOAD_DIR: str = Field(
        default="uploads", description="Local directory for uploaded files."
    )
    MAX_FILE_SIZE_MB: int = Field(
        default=10, description="Maximum file upload size in megabytes."
    )

    # ── Application ────────────────────────────────────────────────────────
    ENVIRONMENT: str = Field(
        default="development",
        description="Runtime environment: development | staging | production.",
    )

    @property
    def is_production(self) -> bool:
        """Convenience property: True when running in production."""
        return self.ENVIRONMENT.lower() == "production"

    @property
    def max_file_size_bytes(self) -> int:
        """Maximum upload size converted to bytes."""
        return self.MAX_FILE_SIZE_MB * 1024 * 1024


@lru_cache()
def get_settings() -> Settings:
    """
    Return a cached singleton instance of Settings.
    Using lru_cache ensures the .env file is read only once.

    Usage:
        from app.core.config import settings
    """
    return Settings()


# Module-level singleton — import this everywhere.
settings: Settings = get_settings()
