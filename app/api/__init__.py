"""
REST API endpoints for Farmers Marketplace.

Implemented endpoints:
- Authentication and user management
- Farmer CRUD operations and search
- Health checks and monitoring (TODO)
- Mobile app optimized endpoints (TODO)
- File upload endpoints for product images (TODO)
- Webhook endpoints for external integrations (TODO)
"""

from .auth import router as auth_router
from .users import router as users_router
from .farmers import router as farmers_router

from typing import List

__all__: List[str] = [
    "auth_router",
    "users_router", 
    "farmers_router",
]
