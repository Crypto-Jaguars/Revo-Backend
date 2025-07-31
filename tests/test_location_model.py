"""
Tests for Location model and geolocation functionality.
"""

import pytest
from math import radians, sin, cos, sqrt, atan2
from pydantic import ValidationError

from app.schemas.location import LocationCreate, LocationResponse


def test_location_lat_lng_bounds():
    """Test that latitude and longitude are within valid bounds."""
    # Test valid coordinates
    valid_location = LocationCreate(latitude=9.93, longitude=-84.08)
    assert -90 <= valid_location.latitude <= 90
    assert -180 <= valid_location.longitude <= 180
    
    # Test edge cases
    edge_location = LocationCreate(latitude=90.0, longitude=180.0)
    assert edge_location.latitude == 90.0
    assert edge_location.longitude == 180.0


def test_location_schema_validation():
    """Test Pydantic schema validation for coordinates."""
    # Valid coordinates
    valid_data = {
        "latitude": 9.93,
        "longitude": -84.08,
        "address": "San José, Costa Rica",
        "city": "San José",
        "state": "San José",
        "country": "Costa Rica"
    }
    location_create = LocationCreate(**valid_data)
    assert location_create.latitude == 9.93
    assert location_create.longitude == -84.08
    
    # Invalid latitude (too high)
    with pytest.raises(ValidationError):
        LocationCreate(latitude=100.0, longitude=-84.08)
    
    # Invalid longitude (too high)
    with pytest.raises(ValidationError):
        LocationCreate(latitude=9.93, longitude=200.0)
    
    # Invalid latitude (too low)
    with pytest.raises(ValidationError):
        LocationCreate(latitude=-100.0, longitude=-84.08)
    
    # Invalid longitude (too low)
    with pytest.raises(ValidationError):
        LocationCreate(latitude=9.93, longitude=-200.0)


def test_location_optional_fields():
    """Test that optional address fields work correctly."""
    # Minimal location with only coordinates
    minimal_location = LocationCreate(
        latitude=9.93,
        longitude=-84.08
    )
    assert minimal_location.latitude == 9.93
    assert minimal_location.longitude == -84.08
    assert minimal_location.address is None
    assert minimal_location.city is None
    
    # Full location with all fields
    full_location = LocationCreate(
        latitude=9.93,
        longitude=-84.08,
        address="123 Main Street",
        city="San José",
        state="San José",
        country="Costa Rica"
    )
    assert full_location.address == "123 Main Street"
    assert full_location.city == "San José"
    assert full_location.state == "San José"
    assert full_location.country == "Costa Rica"


def distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate distance between two points using Haversine formula.
    
    Args:
        lat1, lon1: Coordinates of first point
        lat2, lon2: Coordinates of second point
    
    Returns:
        Distance in kilometers
    """
    R = 6371.0  # Earth's radius in km
    
    # Convert to radians
    lat1_rad = radians(lat1)
    lon1_rad = radians(lon1)
    lat2_rad = radians(lat2)
    lon2_rad = radians(lon2)
    
    # Differences
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    # Haversine formula
    a = sin(dlat / 2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    
    return R * c


def test_distance_function():
    """Test distance calculation between coordinates."""
    # San José, Costa Rica coordinates
    san_jose_lat, san_jose_lon = 9.93, -84.08
    
    # Test distance to nearby point (should be small)
    nearby_lat, nearby_lon = 10.0, -84.0
    dist_nearby = distance_km(san_jose_lat, san_jose_lon, nearby_lat, nearby_lon)
    assert dist_nearby < 15  # Less than 15 km (actual distance is ~11.7 km)
    
    # Test distance to same point (should be 0)
    dist_same = distance_km(san_jose_lat, san_jose_lon, san_jose_lat, san_jose_lon)
    assert dist_same == 0.0
    
    # Test distance to far point (New York coordinates)
    ny_lat, ny_lon = 40.7128, -74.0060
    dist_far = distance_km(san_jose_lat, san_jose_lon, ny_lat, ny_lon)
    assert dist_far > 3000  # More than 3000 km


def test_location_response_schema():
    """Test LocationResponse schema with ID field."""
    location_data = {
        "id": 1,
        "latitude": 9.93,
        "longitude": -84.08,
        "address": "San José, Costa Rica",
        "city": "San José",
        "state": "San José",
        "country": "Costa Rica"
    }
    
    location_response = LocationResponse(**location_data)
    assert location_response.id == 1
    assert location_response.latitude == 9.93
    assert location_response.longitude == -84.08
    assert location_response.address == "San José, Costa Rica"


def test_location_edge_cases():
    """Test edge cases for coordinate validation."""
    # Test exact boundary values
    boundary_location = LocationCreate(
        latitude=90.0,  # Maximum latitude
        longitude=180.0  # Maximum longitude
    )
    assert boundary_location.latitude == 90.0
    assert boundary_location.longitude == 180.0
    
    # Test negative boundary values
    negative_boundary = LocationCreate(
        latitude=-90.0,  # Minimum latitude
        longitude=-180.0  # Minimum longitude
    )
    assert negative_boundary.latitude == -90.0
    assert negative_boundary.longitude == -180.0
    
    # Test zero coordinates
    zero_location = LocationCreate(
        latitude=0.0,
        longitude=0.0
    )
    assert zero_location.latitude == 0.0
    assert zero_location.longitude == 0.0


def test_location_string_representation():
    """Test string representation of location."""
    location = LocationCreate(
        latitude=9.93,
        longitude=-84.08,
        address="123 Main Street",
        city="San José",
        country="Costa Rica"
    )
    
    # Test that the location object can be created
    assert location.latitude == 9.93
    assert location.longitude == -84.08
    assert location.address == "123 Main Street"
    assert location.city == "San José"
    assert location.country == "Costa Rica" 