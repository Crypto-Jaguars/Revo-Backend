from uuid import UUID
from pydantic import BaseModel, Field
from typing import Optional

class FarmerBase(BaseModel):
    farm_name: str
    farm_size: Optional[float] = None
    location: Optional[str] = None
    organic_certified: bool = False
    description: Optional[str] = None

class FarmerCreate(FarmerBase):
    user_id: UUID

class FarmerUpdate(FarmerBase):
    pass

class FarmerResponse(FarmerBase):
    id: UUID
    user_id: UUID

    class Config:
        from_attributes = True 