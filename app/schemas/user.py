from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional
from enum import Enum


class UserType(str, Enum):
    FARMER = "FARMER"
    CONSUMER = "CONSUMER"


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    user_type: UserType


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    user_type: UserType
    is_active: bool
    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: Optional[int] = None
    email: Optional[EmailStr] = None
