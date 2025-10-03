"""
Pydantic schemas for Farmers Marketplace.

TODO: Contributors should implement DTOs/schemas for:
- Product catalog operations
- Order processing
- API request/response models

"""

# TODO: Import schemas as they are implemented
# from .farmer import FarmerCreate, FarmerResponse
# from .product import ProductCreate, ProductResponse

from .farmer import FarmerCreate, FarmerResponse, FarmerUpdate
from .user import Token, TokenData, UserCreate, UserInDB, UserLogin, UserResponse
from .notification import (
    NotificationCreate,
    NotificationResponse,
    NotificationPreferencesUpdate,
    NotificationPreferencesResponse,
    DeviceTokenCreate,
    DeviceTokenResponse,
)

__all__ = [
    # User and Auth schemas
    "UserCreate",
    "UserResponse",
    "UserLogin",
    "Token",
    "TokenData",
    "UserInDB",
    # Farmer schemas
    "FarmerCreate",
    "FarmerResponse", 
    "FarmerUpdate",
    # Notification schemas
    "NotificationCreate",
    "NotificationResponse",
    "NotificationPreferencesUpdate",
    "NotificationPreferencesResponse",
    "DeviceTokenCreate",
    "DeviceTokenResponse",
]
