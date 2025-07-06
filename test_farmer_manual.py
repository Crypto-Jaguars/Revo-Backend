import asyncio
import tempfile
import os
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.models.base import Base
from app.models import User, Farmer
from app.schemas.farmer import FarmerCreate
from app.services.farmer_service import FarmerService

async def test_farmer_implementation():
    """Manual test of farmer implementation."""
    # Create temporary database
    db_fd, db_path = tempfile.mkstemp()
    TEST_DATABASE_URL = f"sqlite+aiosqlite:///{db_path}"
    
    print(f"🔧 Creating test database: {db_path}")
    
    # Create engine and session
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Database tables created")
    
    # Create session
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        try:
            # Test 1: Create a user
            print("\n🧪 Test 1: Creating user...")
            user = User(
                email="testfarmer@example.com",
                username="testfarmer",
                hashed_password="hashedpassword",
                is_active=True
            )
            session.add(user)
            await session.commit()
            await session.refresh(user)
            print(f"✅ User created with ID: {user.id}")
            
            # Test 2: Create farmer profile
            print("\n🧪 Test 2: Creating farmer profile...")
            farmer_service = FarmerService(session)
            
            farmer_data = FarmerCreate(
                farm_name="Green Valley Organic Farm",
                farm_size=45.5,
                location="Sonoma County, California",
                organic_certified=True,
                description="Family-owned organic vegetable and herb farm"
            )
            
            farmer = await farmer_service.create_farmer_profile(user.id, farmer_data)
            print(f"✅ Farmer profile created with ID: {farmer.id}")
            print(f"   Farm name: {farmer.farm_name}")
            print(f"   Farm size: {farmer.farm_size} acres")
            print(f"   Location: {farmer.location}")
            print(f"   Organic certified: {farmer.organic_certified}")
            
            # Test 3: Verify relationship
            print("\n🧪 Test 3: Testing user-farmer relationship...")
            farmer_with_user = await farmer_service.get_farmer_by_id(farmer.id)
            assert farmer_with_user.user.id == user.id
            assert farmer_with_user.user.email == "testfarmer@example.com"
            print("✅ User-farmer relationship working correctly")
            
            # Test 4: Test unique constraint
            print("\n🧪 Test 4: Testing unique farmer per user constraint...")
            try:
                duplicate_farmer_data = FarmerCreate(
                    farm_name="Another Farm",
                    farm_size=20.0,
                    location="Different Location",
                    organic_certified=False,
                    description="This should fail"
                )
                await farmer_service.create_farmer_profile(user.id, duplicate_farmer_data)
                print("❌ ERROR: Should not be able to create duplicate farmer profile")
            except ValueError as e:
                print(f"✅ Unique constraint working: {e}")
            
            # Test 5: Get farmer by user ID
            print("\n🧪 Test 5: Get farmer by user ID...")
            farmer_by_user = await farmer_service.get_farmer_by_user_id(user.id)
            assert farmer_by_user.id == farmer.id
            print("✅ Get farmer by user ID working")
            
            print("\n🎉 All tests passed! Farmer implementation is working correctly.")
            
        except Exception as e:
            print(f"❌ Test failed: {e}")
            import traceback
            traceback.print_exc()
    
    # Cleanup
    await engine.dispose()
    os.close(db_fd)
    os.unlink(db_path)
    print("🧹 Cleanup completed")

if __name__ == "__main__":
    asyncio.run(test_farmer_implementation())
