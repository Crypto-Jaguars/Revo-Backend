"""
User-related models for Farmers Marketplace.

TODO: Contributors should implement:
- UserProfile for additional user data
- UserPreferences for app settings

"""

from sqlalchemy.dialects.postgresql import ENUM

from .user import User, UserType

usertype_enum = ENUM(UserType, name="usertype")

__all__: list[str] = [
    # TODO: Add user model exports as they are implemented
    "User",
    "UserType",
]
