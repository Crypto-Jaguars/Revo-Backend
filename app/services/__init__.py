"""
Business logic services for Farmers Marketplace.

Services implemented:
- Authentication and user management
- Farmer CRUD operations and location-based search
- Product catalog management (TODO)
- Order processing and tracking (TODO)
- Search and filtering operations (TODO)
- Notification services (TODO)
"""

from .auth_service import auth_service
from .farmer_service import FarmerService

__all__ = [
    "auth_service",
    "FarmerService",
]
