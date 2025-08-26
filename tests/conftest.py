"""
Pytest configuration and fixtures - TEMPLATE.
TODO: Expand test fixtures based on business requirements.
"""

import asyncio
import os

import pytest
from httpx import AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.core.database import get_db, get_engine, init_db
from app.main import app
from app.models.base import Base

# Test database URL
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

# Import test models - commented out to avoid table conflicts
# from tests.test_models import TestUser


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def initialize_database():
    """Initialize test database and create tables."""
    # Create test engine
    test_engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        future=True
    )
    
    # Create all tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    # Cleanup: drop all tables and dispose engine
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await test_engine.dispose()
    
    # Remove test database file
    if os.path.exists("./test.db"):
        os.remove("./test.db")


@pytest.fixture
async def db_session(initialize_database):
    """Get database session for testing."""
    # Create test engine and session
    test_engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        future=True
    )
    
    async_session = sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        yield session
        # Clean up after each test
        await session.rollback()
        await session.close()
    
    await test_engine.dispose()


@pytest.fixture
async def client(initialize_database):
    """Get test client."""
    from httpx import ASGITransport

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://testserver"
    ) as async_client:
        yield async_client


@pytest.fixture
def sample_user_data():
    """Sample user data for testing."""
    # TODO: Add authentication and other test utilities.
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpassword123",
        "user_type": "FARMER",
    }


# TODO: Add additional fixtures as needed:
# - Authentication fixtures
# - Database seed data
# - Mock external services
# - Test data factories
# - making push to github
