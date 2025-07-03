"""
Pytest configuration and fixtures - TEMPLATE.
TODO: Expand test fixtures based on business requirements.
"""

import asyncio

import pytest
from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine
import pytest_asyncio

from app.core.config import get_settings
from app.core.database import get_db, init_db
from app.main import app

settings = get_settings()
engine = create_async_engine(settings.database_url, future=True)


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def initialize_database():
    """Initialize test database."""
    # TODO: Customize for specific testing needs.
    await init_db()
    yield
    # TODO: Add cleanup if needed


@pytest.fixture
async def db_session(initialize_database):
    """Get database session for testing."""
    async for session in get_db():
        yield session
        break


@pytest_asyncio.fixture
async def client():
    """Get test client."""
    async with LifespanManager(app):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
            yield ac


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
