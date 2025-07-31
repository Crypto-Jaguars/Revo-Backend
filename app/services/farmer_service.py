"""
Farmer service for business logic operations.

Handles farmer CRUD operations, location-based search, and verification processes.
"""

from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from uuid import UUID
from math import radians, sin, cos, sqrt, atan2

from app.models.farmers.farmer import Farmer
from app.models.shared.location import Location
from app.schemas.farmer import FarmerCreate, FarmerUpdate


class FarmerService:
    """Service class for farmer business logic operations."""
    
    @staticmethod
    async def get_all(db: AsyncSession) -> List[Farmer]:
        """Get all farmers with their location information."""
        result = await db.execute(
            select(Farmer).options(selectinload(Farmer.location))
        )
        return result.scalars().all()

    @staticmethod
    async def get_by_id(db: AsyncSession, farmer_id: UUID) -> Optional[Farmer]:
        """Get a farmer by ID with location information."""
        result = await db.execute(
            select(Farmer)
            .where(Farmer.id == farmer_id)
            .options(selectinload(Farmer.location))
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_user_id(db: AsyncSession, user_id: UUID) -> Optional[Farmer]:
        """Get a farmer by user ID with location information."""
        result = await db.execute(
            select(Farmer)
            .where(Farmer.user_id == user_id)
            .options(selectinload(Farmer.location))
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def create(db: AsyncSession, data: FarmerCreate) -> Farmer:
        """Create a new farmer with optional location."""
        farmer = Farmer(**data.model_dump(exclude={"location"}))
        
        if data.location:
            farmer.location = Location(**data.location.model_dump())
        
        db.add(farmer)
        await db.commit()
        await db.refresh(farmer)
        return farmer

    @staticmethod
    async def update(db: AsyncSession, farmer: Farmer, data: FarmerUpdate) -> Farmer:
        """Update an existing farmer with optional location updates."""
        # Update farmer fields
        for key, value in data.model_dump(exclude_unset=True, exclude={"location"}).items():
            setattr(farmer, key, value)
        
        # Handle location updates
        if data.location:
            if farmer.location:
                # Update existing location
                for key, value in data.location.model_dump(exclude_unset=True).items():
                    setattr(farmer.location, key, value)
            else:
                # Create new location
                farmer.location = Location(**data.location.model_dump())
        
        await db.commit()
        await db.refresh(farmer)
        return farmer

    @staticmethod
    async def delete(db: AsyncSession, farmer: Farmer) -> None:
        """Delete a farmer and associated location."""
        await db.delete(farmer)
        await db.commit()

    @staticmethod
    async def search_by_location(
        db: AsyncSession, 
        lat: float, 
        lng: float, 
        radius_km: float = 50
    ) -> List[Farmer]:
        """
        Search for farmers within a specified radius of given coordinates.
        
        Args:
            db: Database session
            lat: Latitude of search center
            lng: Longitude of search center
            radius_km: Search radius in kilometers (default: 50km)
            
        Returns:
            List of farmers within the specified radius
        """
        def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
            """Calculate distance between two points using Haversine formula."""
            R = 6371  # Earth's radius in kilometers
            
            dlat = radians(lat2 - lat1)
            dlon = radians(lon2 - lon1)
            
            a = (
                sin(dlat / 2) ** 2 + 
                cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
            )
            c = 2 * atan2(sqrt(a), sqrt(1 - a))
            
            return R * c

        # Get all farmers with location data
        result = await db.execute(
            select(Farmer).options(selectinload(Farmer.location))
        )
        all_farmers = result.scalars().all()

        # Filter farmers within the specified radius
        nearby_farmers = []
        for farmer in all_farmers:
            if farmer.location:
                distance = calculate_distance(
                    lat, lng, 
                    farmer.location.latitude, 
                    farmer.location.longitude
                )
                if distance <= radius_km:
                    nearby_farmers.append(farmer)

        return nearby_farmers

    @staticmethod
    async def get_organic_farmers(db: AsyncSession) -> List[Farmer]:
        """Get all organic certified farmers."""
        result = await db.execute(
            select(Farmer)
            .where(Farmer.organic_certified == True)
            .options(selectinload(Farmer.location))
        )
        return result.scalars().all()

    @staticmethod
    async def search_by_farm_name(db: AsyncSession, farm_name: str) -> List[Farmer]:
        """Search farmers by farm name (case-insensitive partial match)."""
        result = await db.execute(
            select(Farmer)
            .where(Farmer.farm_name.ilike(f"%{farm_name}%"))
            .options(selectinload(Farmer.location))
        )
        return result.scalars().all() 