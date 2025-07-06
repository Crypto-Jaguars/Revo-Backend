import pytest
import asyncio
import os
import tempfile
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.models.base import Base
from app.models import User, Farmer
from app.schemas.farmer import FarmerCreate, FarmerUpdate
from app.services.farmer_service import FarmerService

class TestFarmerModel:
    """Standalone farmer model tests."""
    
    @pytest.fixture
    async def db_session(self):
        """Create a test database session."""
        # Create temporary SQLite database
        db_fd, db_path = tempfile.mkstemp()
        TEST_DATABASE_URL = f"sqlite+aiosqlite:///{db_path}"
        
        engine = create_async_engine(TEST_DATABASE_URL, echo=False)
        
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        
        async with async_session() as session:
            yield session
        
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        
        await engine.dispose()
        os.close(db_fd)
        os.unlink(db_path)

    @pytest.mark.asyncio
    async def test_create_farmer_profile(self, db_session: AsyncSession):
        """Test creating a farmer profile."""
        # Create a test user first
        user = User(
            email="farmer@example.com",
            username="testfarmer",
            hashed_password="hashedpass",
            is_active=True
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        
        # Create farmer service
        farmer_service = FarmerService(db_session)
        
        # Create farmer data
        farmer_data = FarmerCreate(
            farm_name="Green Valley Farm",
            farm_size=25.5,
            location="California, USA",
            organic_certified=True,
            description="Organic vegetable farm"
        )
        
        # Create farmer profile
        farmer = await farmer_service.create_farmer_profile(user.id, farmer_data)
        
        assert farmer.id is not None
        assert farmer.user_id == user.id
        assert farmer.farm_name == "Green Valley Farm"
        assert farmer.farm_size == 25.5
        assert farmer.location == "California, USA"
        assert farmer.organic_certified is True
        assert farmer.description == "Organic vegetable farm"
        print("✅ Test create_farmer_profile passed")

    @pytest.mark.asyncio
    async def test_farmer_user_relationship(self, db_session: AsyncSession):
        """Test that farmer profile is correctly linked to user."""
        # Create a test user
        user = User(
            email="farmer2@example.com",
            username="testfarmer2",
            hashed_password="hashedpass",
            is_active=True
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        
        # Create farmer service
        farmer_service = FarmerService(db_session)
        
        # Create farmer profile
        farmer_data = FarmerCreate(
            farm_name="Sunny Acres",
            farm_size=15.0,
            location="Texas, USA",
            organic_certified=False,
            description="Corn and wheat farm"
        )
        
        farmer = await farmer_service.create_farmer_profile(user.id, farmer_data)
        
        # Test relationship
        farmer_with_user = await farmer_service.get_farmer_by_id(farmer.id)
        assert farmer_with_user.user.id == user.id
        assert farmer_with_user.user.email == "farmer2@example.com"
        print("✅ Test farmer_user_relationship passed")

    @pytest.mark.asyncio
    async def test_unique_farmer_per_user(self, db_session: AsyncSession):
        """Test that each user can only have one farmer profile."""
        # Create user
        user = User(
            email="farmer3@example.com",
            username="testfarmer3",
            hashed_password="hashedpass",
            is_active=True
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        
        farmer_service = FarmerService(db_session)
        
        # Create first farmer profile
        farmer_data1 = FarmerCreate(
            farm_name="First Farm",
            farm_size=10.0,
            location="Location 1",
            organic_certified=False,
            description="First farm"
        )
        
        farmer1 = await farmer_service.create_farmer_profile(user.id, farmer_data1)
        assert farmer1 is not None
        
        # Try to create second farmer profile for same user
        farmer_data2 = FarmerCreate(
            farm_name="Second Farm",
            farm_size=20.0,
            location="Location 2",
            organic_certified=True,
            description="Second farm"
        )
        
        with pytest.raises(ValueError, match="Farmer profile already exists"):
            await farmer_service.create_farmer_profile(user.id, farmer_data2)
        print("✅ Test unique_farmer_per_user passed")

# Simple test runner
if __name__ == "__main__":
    print("✅ Standalone test file created successfully")
    print("Run with: pytest tests/test_farmer_standalone.py -v")
