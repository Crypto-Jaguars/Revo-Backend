"""
User-related Pydantic schemas for API requests and responses.
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserBase(BaseModel):
    """Base user schema with common fields."""

    email: EmailStr
    username: str
    is_active: Optional[bool] = True


class UserCreate(UserBase):
    """Schema for user creation."""

    password: str = Field(
        ..., min_length=8, description="Password must be at least 8 characters"
    )  # noqa


class UserLogin(BaseModel):
    """Schema for user login."""

    email: EmailStr
    password: str


class UserResponse(UserBase):
    """Schema for user response."""

    id: int
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserUpdate(BaseModel):
    """Schema for updating user information."""

    email: Optional[EmailStr] = None
    username: Optional[str] = None
    is_active: Optional[bool] = None
    password: Optional[str] = None


class UserInDBBase(UserBase):
    """Schema for user in database (includes password hash)."""

    id: int  # Changed from UUID to int

    class Config:
        orm_mode = True


class User(UserInDBBase):
    """Schema for user."""

    pass


class UserInDB(UserInDBBase):
    """Schema for user in database (includes hashed password)."""

    hashed_password: str


class Token(BaseModel):
    """Token response schema."""

    access_token: str
    token_type: str


class TokenData(BaseModel):
    """Token data schema."""

    email: Optional[str] = None
