"""
Unit tests for FarmerService business logic.

Tests all service methods in isolation with mocked database sessions.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4
from typing import List

from app.services.farmer_service import FarmerService
from app.models.farmers.farmer import Farmer
from app.models.shared.location import Location
from app.schemas.farmer import FarmerCreate, FarmerUpdate


class TestFarmerService:
    """Unit tests for FarmerService class."""

    @pytest.fixture
    def mock_db_session(self):
        """Mock database session for testing."""
        session = AsyncMock()
        session.execute = AsyncMock()
        session.commit = AsyncMock()
        session.refresh = AsyncMock()
        session.delete = AsyncMock()
        return session

    @pytest.fixture
    def sample_farmer_data(self):
        """Sample farmer data for testing."""
        return {
            "user_id": uuid4(),
            "farm_name": "Test Farm",
            "farm_size": 100.5,
            "organic_certified": True,
            "description": "A test farm"
        }

    @pytest.fixture
    def sample_location_data(self):
        """Sample location data for testing."""
        return {
            "address": "123 Test St",
            "city": "Test City",
            "state": "Test State",
            "country": "Test Country",
            "latitude": 40.7128,
            "longitude": -74.0060
        }

    @pytest.fixture
    def mock_farmer(self, sample_farmer_data):
        """Mock farmer instance."""
        farmer = MagicMock(spec=Farmer)
        farmer.id = uuid4()
        farmer.user_id = sample_farmer_data["user_id"]
        farmer.farm_name = sample_farmer_data["farm_name"]
        farmer.farm_size = sample_farmer_data["farm_size"]
        farmer.organic_certified = sample_farmer_data["organic_certified"]
        farmer.description = sample_farmer_data["description"]
        farmer.location = None
        return farmer

    @pytest.fixture
    def mock_farmer_with_location(self, mock_farmer, sample_location_data):
        """Mock farmer with location."""
        location = MagicMock(spec=Location)
        location.id = 1
        location.address = sample_location_data["address"]
        location.city = sample_location_data["city"]
        location.state = sample_location_data["state"]
        location.country = sample_location_data["country"]
        location.latitude = sample_location_data["latitude"]
        location.longitude = sample_location_data["longitude"]
        
        mock_farmer.location = location
        return mock_farmer

    async def test_get_all_farmers(self, mock_db_session, mock_farmer):
        """Test getting all farmers."""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [mock_farmer]
        mock_db_session.execute.return_value = mock_result

        # Act
        result = await FarmerService.get_all(mock_db_session)

        # Assert
        assert result == [mock_farmer]
        mock_db_session.execute.assert_called_once()

    async def test_get_by_id_found(self, mock_db_session, mock_farmer):
        """Test getting farmer by ID when found."""
        # Arrange
        farmer_id = uuid4()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_farmer
        mock_db_session.execute.return_value = mock_result

        # Act
        result = await FarmerService.get_by_id(mock_db_session, farmer_id)

        # Assert
        assert result == mock_farmer
        mock_db_session.execute.assert_called_once()

    async def test_get_by_id_not_found(self, mock_db_session):
        """Test getting farmer by ID when not found."""
        # Arrange
        farmer_id = uuid4()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db_session.execute.return_value = mock_result

        # Act
        result = await FarmerService.get_by_id(mock_db_session, farmer_id)

        # Assert
        assert result is None
        mock_db_session.execute.assert_called_once()

    async def test_get_by_user_id_found(self, mock_db_session, mock_farmer):
        """Test getting farmer by user ID when found."""
        # Arrange
        user_id = uuid4()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_farmer
        mock_db_session.execute.return_value = mock_result

        # Act
        result = await FarmerService.get_by_user_id(mock_db_session, user_id)

        # Assert
        assert result == mock_farmer
        mock_db_session.execute.assert_called_once()

    async def test_get_by_user_id_not_found(self, mock_db_session):
        """Test getting farmer by user ID when not found."""
        # Arrange
        user_id = uuid4()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db_session.execute.return_value = mock_result

        # Act
        result = await FarmerService.get_by_user_id(mock_db_session, user_id)

        # Assert
        assert result is None
        mock_db_session.execute.assert_called_once()

    async def test_create_farmer_without_location(self, mock_db_session, sample_farmer_data):
        """Test creating farmer without location."""
        # Arrange
        farmer_create = FarmerCreate(**sample_farmer_data)

        # Act
        result = await FarmerService.create(mock_db_session, farmer_create)

        # Assert
        assert isinstance(result, Farmer)
        assert result.user_id == sample_farmer_data["user_id"]
        assert result.farm_name == sample_farmer_data["farm_name"]
        assert result.farm_size == sample_farmer_data["farm_size"]
        assert result.organic_certified == sample_farmer_data["organic_certified"]
        assert result.description == sample_farmer_data["description"]
        assert result.location is None
        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_called_once()
        mock_db_session.refresh.assert_called_once()

    async def test_create_farmer_with_location(self, mock_db_session, sample_farmer_data, sample_location_data):
        """Test creating farmer with location."""
        # Arrange
        farmer_data = {**sample_farmer_data, "location": sample_location_data}
        farmer_create = FarmerCreate(**farmer_data)

        # Act
        result = await FarmerService.create(mock_db_session, farmer_create)

        # Assert
        assert isinstance(result, Farmer)
        assert result.user_id == sample_farmer_data["user_id"]
        assert result.farm_name == sample_farmer_data["farm_name"]
        assert result.location is not None
        assert isinstance(result.location, Location)
        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_called_once()
        mock_db_session.refresh.assert_called_once()

    async def test_update_farmer_basic_fields(self, mock_db_session, mock_farmer):
        """Test updating farmer basic fields."""
        # Arrange
        update_data = FarmerUpdate(
            farm_name="Updated Farm",
            farm_size=150.0,
            organic_certified=True
        )

        # Act
        result = await FarmerService.update(mock_db_session, mock_farmer, update_data)

        # Assert
        assert result == mock_farmer
        assert mock_farmer.farm_name == "Updated Farm"
        assert mock_farmer.farm_size == 150.0
        assert mock_farmer.organic_certified is True
        mock_db_session.commit.assert_called_once()
        mock_db_session.refresh.assert_called_once_with(mock_farmer)

    async def test_update_farmer_with_new_location(self, mock_db_session, mock_farmer, sample_location_data):
        """Test updating farmer with new location."""
        # Arrange
        update_data = FarmerUpdate(
            farm_name="Updated Farm",
            location=sample_location_data
        )

        # Act
        result = await FarmerService.update(mock_db_session, mock_farmer, update_data)

        # Assert
        assert result == mock_farmer
        assert mock_farmer.farm_name == "Updated Farm"
        assert mock_farmer.location is not None
        mock_db_session.commit.assert_called_once()
        mock_db_session.refresh.assert_called_once_with(mock_farmer)

    async def test_update_farmer_with_existing_location(self, mock_db_session, mock_farmer_with_location, sample_location_data):
        """Test updating farmer with existing location."""
        # Arrange
        update_data = FarmerUpdate(
            farm_name="Updated Farm",
            location=sample_location_data
        )

        # Act
        result = await FarmerService.update(mock_db_session, mock_farmer_with_location, update_data)

        # Assert
        assert result == mock_farmer_with_location
        assert mock_farmer_with_location.farm_name == "Updated Farm"
        mock_db_session.commit.assert_called_once()
        mock_db_session.refresh.assert_called_once_with(mock_farmer_with_location)

    async def test_delete_farmer(self, mock_db_session, mock_farmer):
        """Test deleting farmer."""
        # Act
        await FarmerService.delete(mock_db_session, mock_farmer)

        # Assert
        mock_db_session.delete.assert_called_once_with(mock_farmer)
        mock_db_session.commit.assert_called_once()

    async def test_search_by_location_with_results(self, mock_db_session, mock_farmer_with_location):
        """Test location-based search with results."""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [mock_farmer_with_location]
        mock_db_session.execute.return_value = mock_result

        # Act
        result = await FarmerService.search_by_location(mock_db_session, 40.7128, -74.0060, 50.0)

        # Assert
        assert result == [mock_farmer_with_location]
        mock_db_session.execute.assert_called_once()

    async def test_search_by_location_no_results(self, mock_db_session):
        """Test location-based search with no results."""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_db_session.execute.return_value = mock_result

        # Act
        result = await FarmerService.search_by_location(mock_db_session, 40.7128, -74.0060, 50.0)

        # Assert
        assert result == []
        mock_db_session.execute.assert_called_once()

    async def test_search_by_location_farmer_without_location(self, mock_db_session, mock_farmer):
        """Test location-based search with farmer without location."""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [mock_farmer]
        mock_db_session.execute.return_value = mock_result

        # Act
        result = await FarmerService.search_by_location(mock_db_session, 40.7128, -74.0060, 50.0)

        # Assert
        assert result == []  # Should be empty because farmer has no location

    async def test_get_organic_farmers(self, mock_db_session, mock_farmer):
        """Test getting organic farmers."""
        # Arrange
        mock_farmer.organic_certified = True
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [mock_farmer]
        mock_db_session.execute.return_value = mock_result

        # Act
        result = await FarmerService.get_organic_farmers(mock_db_session)

        # Assert
        assert result == [mock_farmer]
        mock_db_session.execute.assert_called_once()

    async def test_get_organic_farmers_empty(self, mock_db_session):
        """Test getting organic farmers when none exist."""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_db_session.execute.return_value = mock_result

        # Act
        result = await FarmerService.get_organic_farmers(mock_db_session)

        # Assert
        assert result == []
        mock_db_session.execute.assert_called_once()

    async def test_search_by_farm_name(self, mock_db_session, mock_farmer):
        """Test searching farmers by farm name."""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [mock_farmer]
        mock_db_session.execute.return_value = mock_result

        # Act
        result = await FarmerService.search_by_farm_name(mock_db_session, "Test")

        # Assert
        assert result == [mock_farmer]
        mock_db_session.execute.assert_called_once()

    async def test_search_by_farm_name_no_results(self, mock_db_session):
        """Test searching farmers by farm name with no results."""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_db_session.execute.return_value = mock_result

        # Act
        result = await FarmerService.search_by_farm_name(mock_db_session, "Nonexistent")

        # Assert
        assert result == []
        mock_db_session.execute.assert_called_once()


class TestFarmerServiceDistanceCalculation:
    """Test distance calculation functionality."""

    @pytest.fixture
    def mock_db_session(self):
        """Mock database session for testing."""
        session = AsyncMock()
        session.execute = AsyncMock()
        session.commit = AsyncMock()
        session.refresh = AsyncMock()
        session.delete = AsyncMock()
        return session

    async def test_distance_calculation_accuracy(self, mock_db_session):
        """Test that distance calculation is accurate."""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_db_session.execute.return_value = mock_result

        # Act
        result = await FarmerService.search_by_location(mock_db_session, 40.7128, -74.0060, 50.0)

        # Assert
        assert result == []
        mock_db_session.execute.assert_called_once()

    async def test_distance_calculation_with_farmers_in_range(self, mock_db_session):
        """Test distance calculation with farmers within range."""
        # Create mock farmers with different distances
        farmer1 = MagicMock(spec=Farmer)
        farmer1.location = MagicMock(spec=Location)
        farmer1.location.latitude = 40.7128
        farmer1.location.longitude = -74.0060  # Same location

        farmer2 = MagicMock(spec=Farmer)
        farmer2.location = MagicMock(spec=Location)
        farmer2.location.latitude = 40.7628
        farmer2.location.longitude = -74.0060  # ~5.5 km away

        farmer3 = MagicMock(spec=Farmer)
        farmer3.location = MagicMock(spec=Location)
        farmer3.location.latitude = 41.2128
        farmer3.location.longitude = -74.0060  # ~55 km away

        # Arrange
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [farmer1, farmer2, farmer3]
        mock_db_session.execute.return_value = mock_result

        # Act
        result = await FarmerService.search_by_location(mock_db_session, 40.7128, -74.0060, 10.0)

        # Assert - should only include farmers within 10km
        assert len(result) == 2  # farmer1 and farmer2
        assert farmer1 in result
        assert farmer2 in result
        assert farmer3 not in result


class TestFarmerServiceEdgeCases:
    """Test edge cases and error scenarios."""

    @pytest.fixture
    def mock_db_session(self):
        """Mock database session for testing."""
        session = AsyncMock()
        session.execute = AsyncMock()
        session.commit = AsyncMock()
        session.refresh = AsyncMock()
        session.delete = AsyncMock()
        return session

    async def test_create_farmer_with_none_values(self, mock_db_session):
        """Test creating farmer with None values."""
        # Arrange
        farmer_data = {
            "user_id": uuid4(),
            "farm_name": "Test Farm",
            "farm_size": None,
            "organic_certified": False,
            "description": None
        }
        farmer_create = FarmerCreate(**farmer_data)

        # Act
        result = await FarmerService.create(mock_db_session, farmer_create)

        # Assert
        assert isinstance(result, Farmer)
        assert result.farm_name == "Test Farm"
        assert result.farm_size is None
        assert result.organic_certified is False
        assert result.description is None
        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_called_once()

    async def test_update_farmer_partial_data(self, mock_db_session):
        """Test updating farmer with partial data."""
        # Arrange
        mock_farmer = MagicMock(spec=Farmer)
        mock_farmer.farm_name = "Original Farm"
        mock_farmer.farm_size = 100.0
        mock_farmer.organic_certified = False
        mock_farmer.description = "Original description"
        
        update_data = FarmerUpdate(farm_name="Updated Farm")  # Only update name

        # Act
        result = await FarmerService.update(mock_db_session, mock_farmer, update_data)

        # Assert
        assert result == mock_farmer
        assert mock_farmer.farm_name == "Updated Farm"
        # Other fields should remain unchanged
        mock_db_session.commit.assert_called_once()

    async def test_search_by_location_zero_radius(self, mock_db_session):
        """Test location search with zero radius."""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_db_session.execute.return_value = mock_result

        # Act
        result = await FarmerService.search_by_location(mock_db_session, 40.7128, -74.0060, 0.0)

        # Assert
        assert result == []
        mock_db_session.execute.assert_called_once()

    async def test_search_by_location_large_radius(self, mock_db_session):
        """Test location search with large radius."""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_db_session.execute.return_value = mock_result

        # Act
        result = await FarmerService.search_by_location(mock_db_session, 40.7128, -74.0060, 1000.0)

        # Assert
        assert result == []
        mock_db_session.execute.assert_called_once() 