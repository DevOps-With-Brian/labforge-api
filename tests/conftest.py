"""Pytest configuration and fixtures for tests."""

import os

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.db.models import Base
from app.db.session import get_session
from app.main import app


def get_table_names() -> list[str]:
    """Get all table names from SQLAlchemy metadata."""
    return list(Base.metadata.tables.keys())

# Configure test database to use NullPool for connection isolation
test_engine = create_async_engine(
    os.getenv(
        "DATABASE_URL", "postgresql+asyncpg://labforge:labforge@localhost:5432/labforge"
    ),
    poolclass=NullPool,  # Don't pool connections in tests
    echo=False,
)
test_session_factory = async_sessionmaker(
    bind=test_engine,
    expire_on_commit=False,
)


async def override_get_session():
    """Override session for tests with proper connection isolation."""
    async with test_session_factory() as session:
        yield session


# Override the dependency
app.dependency_overrides[get_session] = override_get_session


@pytest.fixture(autouse=True, scope="function")
def reset_db():
    """Reset database tables between tests using a sync connection."""
    # Convert async URL to sync URL for test cleanup
    db_url = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://labforge:labforge@localhost:5432/labforge",
    ).replace("postgresql+asyncpg://", "postgresql+psycopg://")

    sync_engine = create_engine(
        db_url,
        poolclass=NullPool,
        echo=False,
    )

    # Build truncate statement dynamically from metadata
    table_names = ", ".join(get_table_names())
    truncate_stmt = f"TRUNCATE TABLE {table_names} RESTART IDENTITY CASCADE"

    # Truncate tables before test
    with sync_engine.connect() as conn:
        conn.execute(text(truncate_stmt))
        conn.commit()

    yield

    # Truncate tables after test
    with sync_engine.connect() as conn:
        conn.execute(text(truncate_stmt))
        conn.commit()

    sync_engine.dispose()
