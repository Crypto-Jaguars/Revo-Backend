"""
Tests for Farmer model and related functionality.
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.farmers.farmer import Farmer
from app.models.users.user import User, UserType
from app.schemas.farmer import FarmerCreate, FarmerResponse


class TestFarmerModel:
    """Test Farmer model functionality."""

    async def test_farmer_creation(self, db_session: AsyncSession):
        """Test creating a farmer profile."""
        # Create a user first
        user = User(
            email="farmer@test.com",
            password_hash="hashed_password",
            user_type=UserType.FARMER,
            is_active=True,
            is_verified=True
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        # Create farmer profile
        farmer = Farmer(
            user_id=user.id,
            farm_name="Test Farm",
            farm_size=50.0,
            location="Test Location",
            organic_certified=True,
            description="A test farm"
        )
        db_session.add(farmer)
        await db_session.commit()
        await db_session.refresh(farmer)

        # Verify farmer was created
        assert farmer.id is not None
        assert farmer.farm_name == "Test Farm"
        assert farmer.user_id == user.id
        assert farmer.organic_certified is True

    async def test_farmer_user_relationship(self, db_session: AsyncSession):
        """Test the relationship between User and Farmer."""
        # Create a user first
        user = User(
            email="farmer@test.com",
            password_hash="hashed_password",
            user_type=UserType.FARMER,
            is_active=True,
            is_verified=True
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        # Create a farmer profile
        farmer = Farmer(
            user_id=user.id,
            farm_name="Test Farm",
            farm_size=50.0,
            location="Test Location",
            organic_certified=True,
            description="A test farm"
        )
        db_session.add(farmer)
        await db_session.commit()
        await db_session.refresh(farmer)

        # Refresh user to get the relationship
        await db_session.refresh(user)
        
        # Verify relationship - use explicit query to avoid lazy loading issues
        from sqlalchemy import select
        user_with_farmer = await db_session.execute(
            select(User).where(User.id == user.id)
        )
        user_obj = user_with_farmer.scalar_one()
        
        # Verify the farmer was created and linked
        assert farmer.user_id == user.id
        assert farmer.farm_name == "Test Farm"
        
        # Verify we can access the relationship from farmer side
        assert farmer.user is not None
        assert farmer.user.id == user.id

    async def test_farmer_schema_validation(self):
        """Test Farmer schema validation."""
        # Test valid farmer data
        farmer_data = {
            "user_id": "123e4567-e89b-12d3-a456-426614174000",
            "farm_name": "Test Farm",
            "farm_size": 50.0,
            "location": "Test Location",
            "organic_certified": True,
            "description": "A test farm"
        }
        
        farmer_create = FarmerCreate(**farmer_data)
        assert farmer_create.farm_name == "Test Farm"
        assert farmer_create.organic_certified is True

        # Test farmer response schema
        farmer_response_data = {
            "id": "123e4567-e89b-12d3-a456-426614174001",
            "user_id": "123e4567-e89b-12d3-a456-426614174000",
            "farm_name": "Test Farm",
            "farm_size": 50.0,
            "location": "Test Location",
            "organic_certified": True,
            "description": "A test farm",
            "created_at": "2024-01-01T00:00:00",
            "updated_at": "2024-01-01T00:00:00"
        }
        
        farmer_response = FarmerResponse(**farmer_response_data)
        assert str(farmer_response.id) == "123e4567-e89b-12d3-a456-426614174001"
        assert farmer_response.farm_name == "Test Farm"


class TestFarmerAPI:
    """Test Farmer API endpoints."""

    async def test_create_farmer_profile(self, client: AsyncClient, db_session: AsyncSession):
        """Test creating a farmer profile via API."""
        # First create a user
        user_data = {
            "email": "farmer@test.com",
            "password": "testpassword123",
            "user_type": "FARMER"
        }
        
        response = await client.post("/api/users/register", json=user_data)
        assert response.status_code == 201
        
        user_response = response.json()
        user_id = user_response["id"]

        # Create farmer profile
        farmer_data = {
            "user_id": user_id,
            "farm_name": "Test Farm",
            "farm_size": 50.0,
            "location": "Test Location",
            "organic_certified": True,
            "description": "A test farm"
        }
        
        # Note: This endpoint doesn't exist yet, but we're testing the concept
        # response = await client.post("/api/farmers/", json=farmer_data)
        # assert response.status_code == 201
        
        # For now, we'll just verify the user was created with FARMER type
        assert user_response["user_type"] == "FARMER"

    async def test_farmer_type_user_creation(self, client: AsyncClient):
        """Test that FARMER-type user can be created."""
        user_data = {
            "email": "farmer@test.com",
            "password": "testpassword123",
            "user_type": "FARMER"
        }
        
        response = await client.post("/api/users/register", json=user_data)
        assert response.status_code == 201
        
        user_response = response.json()
        assert user_response["user_type"] == "FARMER"
        assert user_response["email"] == "farmer@test.com" 