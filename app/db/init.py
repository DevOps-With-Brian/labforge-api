"""Database initialization helpers."""

from app.db.models import Base
from app.db.session import engine


async def init_db() -> None:
    """Create tables if they do not exist (dev/test convenience)."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def reset_db() -> None:
    """Drop and recreate tables (used in tests)."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
