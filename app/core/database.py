"""
Database connection and session management.
"""

from typing import AsyncGenerator, Optional

from loguru import logger
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import declarative_base

from app.core.config import get_settings

# Base class for SQLAlchemy models
Base = declarative_base()

# Global variables
engine = None
SessionLocal: Optional[async_sessionmaker[AsyncSession]] = None


async def init_db():
    """Initialize database connection."""
    global engine, SessionLocal

    settings = get_settings()

    # Create async engine
    engine = create_async_engine(
        settings.database_url,
        echo=settings.is_development,
        future=True,
    )

    # Create session factory
    SessionLocal = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    logger.info("Database connection initialized")


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Get database session."""
    if SessionLocal is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    async with SessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


def get_engine():
    """Get database engine."""
    return engine
