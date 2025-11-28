"""Application configuration settings."""

import os
from functools import lru_cache

from dotenv import load_dotenv
from pydantic import BaseModel, Field

# Load .env if present to support local development and Alembic.
load_dotenv()


class Settings(BaseModel):
    """Lightweight settings container."""

    database_url: str = Field(
        default=os.getenv(
            "DATABASE_URL",
            "sqlite+aiosqlite:///./labforge.db",
        )
    )


@lru_cache
def get_settings() -> Settings:
    """Return cached settings instance."""
    return Settings()


settings = get_settings()
