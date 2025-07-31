"""
Comprehensive integration tests for Farmers API endpoints.

Tests CRUD operations, search functionality, authentication,
and authorization for farmer profiles.
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import uuid4


class TestFarmerCRUD:
    """Test farmer CRUD operations."""

    async def test_list_farmers_empty(self, client: AsyncClient, db_session: AsyncSession):
        """Test listing farmers when database is empty."""
        response = await client.get("/api/farmers/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0

    async def test_get_farmer_not_found(self, client: AsyncClient, db_session: AsyncSession):
        """Test getting a non-existent farmer."""
        farmer_id = str(uuid4())
        response = await client.get(f"/api/farmers/{farmer_id}")
        assert response.status_code == 404
        assert "Farmer not found" in response.json()["detail"]

    async def test_create_farmer_unauthorized(self, client: AsyncClient, db_session: AsyncSession):
        """Test creating farmer without authentication."""
        farmer_data = {
            "user_id": str(uuid4()),
            "farm_name": "Test Farm",
            "farm_size": 100.5,
            "organic_certified": True,
            "description": "A test farm"
        }
        response = await client.post("/api/farmers/", json=farmer_data)
        assert response.status_code == 401

    async def test_create_farmer_success(self, client: AsyncClient, db_session: AsyncSession):
        """Test successful farmer creation with authentication."""
        # First create a user
        user_data = {
            "email": "farmer@test.com",
            "password": "testpassword123",
            "user_type": "FARMER"
        }
        user_response = await client.post("/api/users/register", json=user_data)
        assert user_response.status_code == 201
        user_id = user_response.json()["id"]

        # Login to get token
        login_data = {
            "email": "farmer@test.com",
            "password": "testpassword123"
        }
        login_response = await client.post("/api/users/login", json=login_data)
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]

        # Create farmer profile
        farmer_data = {
            "user_id": user_id,
            "farm_name": "Green Valley Farm",
            "farm_size": 150.0,
            "organic_certified": True,
            "description": "Organic vegetables and fruits"
        }
        headers = {"Authorization": f"Bearer {token}"}
        response = await client.post("/api/farmers/", json=farmer_data, headers=headers)
        
        assert response.status_code == 201
        data = response.json()
        assert data["farm_name"] == farmer_data["farm_name"]
        assert data["farm_size"] == farmer_data["farm_size"]
        assert data["organic_certified"] == farmer_data["organic_certified"]
        assert data["user_id"] == user_id
        assert "id" in data

    async def test_create_farmer_duplicate_profile(self, client: AsyncClient, db_session: AsyncSession):
        """Test creating duplicate farmer profile for same user."""
        # Create user and login
        user_data = {
            "email": "duplicate@test.com",
            "password": "testpassword123",
            "user_type": "FARMER"
        }
        user_response = await client.post("/api/users/register", json=user_data)
        user_id = user_response.json()["id"]

        login_response = await client.post("/api/users/login", json={
            "email": "duplicate@test.com",
            "password": "testpassword123"
        })
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Create first farmer profile
        farmer_data = {
            "user_id": user_id,
            "farm_name": "First Farm",
            "farm_size": 100.0
        }
        response1 = await client.post("/api/farmers/", json=farmer_data, headers=headers)
        assert response1.status_code == 201

        # Try to create second profile for same user
        response2 = await client.post("/api/farmers/", json=farmer_data, headers=headers)
        assert response2.status_code == 409
        assert "already has a farmer profile" in response2.json()["detail"]

    async def test_create_farmer_wrong_user(self, client: AsyncClient, db_session: AsyncSession):
        """Test creating farmer profile for different user."""
        # Create two users
        user1_data = {"email": "user1@test.com", "password": "testpassword123", "user_type": "FARMER"}
        user2_data = {"email": "user2@test.com", "password": "testpassword123", "user_type": "FARMER"}
        
        user1_response = await client.post("/api/users/register", json=user1_data)
        user2_response = await client.post("/api/users/register", json=user2_data)
        user1_id = user1_response.json()["id"]
        user2_id = user2_response.json()["id"]

        # Login as user1
        login_response = await client.post("/api/users/login", json={
            "email": "user1@test.com",
            "password": "testpassword123"
        })
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Try to create farmer profile for user2
        farmer_data = {
            "user_id": user2_id,
            "farm_name": "Wrong Farm",
            "farm_size": 100.0
        }
        response = await client.post("/api/farmers/", json=farmer_data, headers=headers)
        assert response.status_code == 403
        assert "Cannot create profile for another user" in response.json()["detail"]


class TestFarmerSearch:
    """Test farmer search functionality."""

    async def test_search_by_location_success(self, client: AsyncClient, db_session: AsyncSession):
        """Test location-based search."""
        response = await client.get("/api/farmers/search/location/", params={
            "lat": 40.7128,
            "lng": -74.0060,
            "radius": 50.0
        })
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    async def test_search_by_location_missing_params(self, client: AsyncClient, db_session: AsyncSession):
        """Test location search with missing parameters."""
        response = await client.get("/api/farmers/search/location/", params={"lat": 40.7128})
        assert response.status_code == 422

    async def test_search_by_location_invalid_radius(self, client: AsyncClient, db_session: AsyncSession):
        """Test location search with invalid radius."""
        response = await client.get("/api/farmers/search/location/", params={
            "lat": 40.7128,
            "lng": -74.0060,
            "radius": -10.0
        })
        assert response.status_code == 422

    async def test_search_by_name_success(self, client: AsyncClient, db_session: AsyncSession):
        """Test name-based search."""
        response = await client.get("/api/farmers/search/name/", params={"farm_name": "test"})
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    async def test_search_by_name_empty_query(self, client: AsyncClient, db_session: AsyncSession):
        """Test name search with empty query."""
        response = await client.get("/api/farmers/search/name/", params={"farm_name": ""})
        assert response.status_code == 422

    async def test_get_organic_farmers(self, client: AsyncClient, db_session: AsyncSession):
        """Test getting organic farmers."""
        response = await client.get("/api/farmers/organic/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


class TestFarmerAuthentication:
    """Test farmer endpoints with authentication."""

    async def test_get_my_profile_unauthorized(self, client: AsyncClient, db_session: AsyncSession):
        """Test getting own profile without authentication."""
        response = await client.get("/api/farmers/me/profile")
        assert response.status_code == 401

    async def test_get_my_profile_no_profile(self, client: AsyncClient, db_session: AsyncSession):
        """Test getting own profile when user has no farmer profile."""
        # Create user and login
        user_data = {
            "email": "noprofile@test.com",
            "password": "testpassword123",
            "user_type": "FARMER"
        }
        await client.post("/api/users/register", json=user_data)
        
        login_response = await client.post("/api/users/login", json={
            "email": "noprofile@test.com",
            "password": "testpassword123"
        })
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        response = await client.get("/api/farmers/me/profile", headers=headers)
        assert response.status_code == 404
        assert "No farmer profile found" in response.json()["detail"]

    async def test_get_my_profile_success(self, client: AsyncClient, db_session: AsyncSession):
        """Test getting own profile successfully."""
        # Create user and login
        user_data = {
            "email": "myprofile@test.com",
            "password": "testpassword123",
            "user_type": "FARMER"
        }
        user_response = await client.post("/api/users/register", json=user_data)
        user_id = user_response.json()["id"]

        login_response = await client.post("/api/users/login", json={
            "email": "myprofile@test.com",
            "password": "testpassword123"
        })
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Create farmer profile
        farmer_data = {
            "user_id": user_id,
            "farm_name": "My Farm",
            "farm_size": 75.0,
            "organic_certified": False
        }
        await client.post("/api/farmers/", json=farmer_data, headers=headers)

        # Get own profile
        response = await client.get("/api/farmers/me/profile", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["farm_name"] == "My Farm"
        assert data["user_id"] == user_id


class TestFarmerUpdateDelete:
    """Test farmer update and delete operations."""

    async def test_update_farmer_unauthorized(self, client: AsyncClient, db_session: AsyncSession):
        """Test updating farmer without authentication."""
        farmer_id = str(uuid4())
        update_data = {"farm_name": "Updated Farm"}
        response = await client.put(f"/api/farmers/{farmer_id}", json=update_data)
        assert response.status_code == 401

    async def test_update_farmer_not_found(self, client: AsyncClient, db_session: AsyncSession):
        """Test updating non-existent farmer."""
        # Create user and login
        user_data = {
            "email": "update@test.com",
            "password": "testpassword123",
            "user_type": "FARMER"
        }
        await client.post("/api/users/register", json=user_data)
        
        login_response = await client.post("/api/users/login", json={
            "email": "update@test.com",
            "password": "testpassword123"
        })
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        farmer_id = str(uuid4())
        update_data = {"farm_name": "Updated Farm"}
        response = await client.put(f"/api/farmers/{farmer_id}", json=update_data, headers=headers)
        assert response.status_code == 404

    async def test_update_farmer_success(self, client: AsyncClient, db_session: AsyncSession):
        """Test successful farmer update."""
        # Create user and farmer profile
        user_data = {
            "email": "update@test.com",
            "password": "testpassword123",
            "user_type": "FARMER"
        }
        user_response = await client.post("/api/users/register", json=user_data)
        user_id = user_response.json()["id"]

        login_response = await client.post("/api/users/login", json={
            "email": "update@test.com",
            "password": "testpassword123"
        })
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Create farmer profile
        farmer_data = {
            "user_id": user_id,
            "farm_name": "Original Farm",
            "farm_size": 100.0
        }
        create_response = await client.post("/api/farmers/", json=farmer_data, headers=headers)
        farmer_id = create_response.json()["id"]

        # Update farmer
        update_data = {
            "farm_name": "Updated Farm",
            "farm_size": 150.0,
            "organic_certified": True
        }
        response = await client.put(f"/api/farmers/{farmer_id}", json=update_data, headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["farm_name"] == "Updated Farm"
        assert data["farm_size"] == 150.0
        assert data["organic_certified"] is True

    async def test_delete_farmer_unauthorized(self, client: AsyncClient, db_session: AsyncSession):
        """Test deleting farmer without authentication."""
        farmer_id = str(uuid4())
        response = await client.delete(f"/api/farmers/{farmer_id}")
        assert response.status_code == 401

    async def test_delete_farmer_success(self, client: AsyncClient, db_session: AsyncSession):
        """Test successful farmer deletion."""
        # Create user and farmer profile
        user_data = {
            "email": "delete@test.com",
            "password": "testpassword123",
            "user_type": "FARMER"
        }
        user_response = await client.post("/api/users/register", json=user_data)
        user_id = user_response.json()["id"]

        login_response = await client.post("/api/users/login", json={
            "email": "delete@test.com",
            "password": "testpassword123"
        })
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Create farmer profile
        farmer_data = {
            "user_id": user_id,
            "farm_name": "Delete Farm",
            "farm_size": 100.0
        }
        create_response = await client.post("/api/farmers/", json=farmer_data, headers=headers)
        farmer_id = create_response.json()["id"]

        # Delete farmer
        response = await client.delete(f"/api/farmers/{farmer_id}", headers=headers)
        assert response.status_code == 204

        # Verify farmer is deleted
        get_response = await client.get(f"/api/farmers/{farmer_id}")
        assert get_response.status_code == 404


class TestFarmerPagination:
    """Test farmer list pagination."""

    async def test_list_farmers_with_pagination(self, client: AsyncClient, db_session: AsyncSession):
        """Test farmer list with pagination parameters."""
        response = await client.get("/api/farmers/", params={"skip": 0, "limit": 10})
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    async def test_list_farmers_invalid_pagination(self, client: AsyncClient, db_session: AsyncSession):
        """Test farmer list with invalid pagination parameters."""
        response = await client.get("/api/farmers/", params={"skip": -1, "limit": 10})
        assert response.status_code == 422

        response = await client.get("/api/farmers/", params={"skip": 0, "limit": 0})
        assert response.status_code == 422 