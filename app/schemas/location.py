"""
Location schemas for API requests and responses.
"""

from typing import Optional
from pydantic import BaseModel, Field


class LocationBase(BaseModel):
    """Base location schema with common fields."""
    
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    latitude: float = Field(..., ge=-90, le=90, description="Latitude coordinate")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude coordinate")


class LocationCreate(LocationBase):
    """Schema for creating a new location."""
    pass


class LocationUpdate(LocationBase):
    """Schema for updating an existing location."""
    pass


class LocationResponse(LocationBase):
    """Schema for location response."""
    id: int

    class Config:
        from_attributes = True 