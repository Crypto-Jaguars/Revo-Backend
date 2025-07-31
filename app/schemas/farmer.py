from uuid import UUID
from pydantic import BaseModel, Field
from typing import Optional

from app.schemas.location import LocationCreate, LocationResponse

class FarmerBase(BaseModel):
    farm_name: str
    farm_size: Optional[float] = None
    organic_certified: bool = False
    description: Optional[str] = None

class FarmerCreate(FarmerBase):
    user_id: UUID
    location: Optional[LocationCreate] = None

class FarmerUpdate(FarmerBase):
    location: Optional[LocationCreate] = None

class FarmerResponse(FarmerBase):
    id: UUID
    user_id: UUID
    location: Optional[LocationResponse] = None

    class Config:
        from_attributes = True 