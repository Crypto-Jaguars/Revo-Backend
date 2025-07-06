from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, validator


class FarmerBase(BaseModel):
    farm_name: str = Field(..., min_length=1, max_length=255, description="Name of the farm")
    farm_size: Optional[float] = Field(None, ge=0, description="Farm size in acres/hectares")
    location: Optional[str] = Field(None, max_length=500, description="Farm location")
    organic_certified: bool = Field(False, description="Whether the farm is organic certified")
    description: Optional[str] = Field(None, description="Farm description")

    @validator('farm_name')
    def validate_farm_name(cls, v):
        if not v or not v.strip():
            raise ValueError('Farm name cannot be empty')
        return v.strip()

    @validator('farm_size')
    def validate_farm_size(cls, v):
        if v is not None and v < 0:
            raise ValueError('Farm size must be non-negative')
        return v


class FarmerCreate(FarmerBase):
    pass


class FarmerUpdate(BaseModel):
    farm_name: Optional[str] = Field(None, min_length=1, max_length=255)
    farm_size: Optional[float] = Field(None, ge=0)
    location: Optional[str] = Field(None, max_length=500)
    organic_certified: Optional[bool] = None
    description: Optional[str] = None

    @validator('farm_name')
    def validate_farm_name(cls, v):
        if v is not None and (not v or not v.strip()):
            raise ValueError('Farm name cannot be empty')
        return v.strip() if v else v

    @validator('farm_size')
    def validate_farm_size(cls, v):
        if v is not None and v < 0:
            raise ValueError('Farm size must be non-negative')
        return v


class FarmerResponse(FarmerBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True
        from_attributes = True
