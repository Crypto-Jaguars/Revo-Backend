from __future__ import annotations
from typing import Optional, TYPE_CHECKING
from uuid import UUID
from datetime import datetime

import strawberry

if TYPE_CHECKING:
    from app.models.farmers.farmer import Farmer as FarmerModel
    from app.models.shared.location import Location as LocationModel

@strawberry.type
class Location:
    id: int
    address: Optional[str]
    city: Optional[str]
    state: Optional[str]
    country: Optional[str]
    latitude: float
    longitude: float

    @classmethod
    def from_model(cls, loc: "LocationModel") -> "Location":
        return cls(
            id=loc.id,
            address=loc.address,
            city=loc.city,
            state=loc.state,
            country=loc.country,
            latitude=loc.latitude,
            longitude=loc.longitude,
        )

@strawberry.type
class Farmer:
    id: UUID
    user_id: UUID
    farm_name: str
    farm_size: Optional[float]
    organic_certified: bool
    description: Optional[str]
    created_at: datetime
    updated_at: datetime
    location: Optional[Location]

    @classmethod
    def from_model(cls, f: "FarmerModel") -> "Farmer":
        return cls(
            id=f.id,
            user_id=f.user_id,
            farm_name=f.farm_name,
            farm_size=f.farm_size,
            organic_certified=f.organic_certified,
            description=f.description,
            created_at=f.created_at,
            updated_at=f.updated_at,
            location=Location.from_model(f.location) if getattr(f, "location", None) else None,
        )

@strawberry.input
class LocationInput:
    # minimal for create; optional address metadata
    latitude: float
    longitude: float
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None

@strawberry.input
class FarmerInput:
    user_id: UUID
    farm_name: str
    farm_size: Optional[float] = None
    organic_certified: bool = False
    description: Optional[str] = None
    location: Optional[LocationInput] = None

@strawberry.input
class FarmerUpdateInput:
    farm_name: Optional[str] = None
    farm_size: Optional[float] = None
    organic_certified: Optional[bool] = None
    description: Optional[str] = None
    location: Optional[LocationInput] = None
