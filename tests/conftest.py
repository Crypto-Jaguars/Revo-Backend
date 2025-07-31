"""
Pytest configuration and fixtures - TEMPLATE.
TODO: Expand test fixtures based on business requirements.
"""

import asyncio

import pytest
from httpx import AsyncClient
from sqlalchemy import text

from app.core.database import get_db, get_engine, init_db
from app.main import app
from app.models.base import Base


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def initialize_database():
    """Initialize test database and create tables."""
    # Initialize database connection
    await init_db()

    # Get engine and create all tables
    engine = get_engine()
    if engine:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    yield

    # Cleanup: drop all tables
    if engine:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        await engine.dispose()


@pytest.fixture
async def db_session(initialize_database):
    """Get database session for testing."""
    async for session in get_db():
        yield session
        # Clean up after each test by truncating the users table
        await session.execute(text("TRUNCATE TABLE users RESTART IDENTITY CASCADE"))
        await session.commit()
        break


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
