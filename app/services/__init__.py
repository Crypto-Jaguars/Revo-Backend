"""
Business logic services for Farmers Marketplace.

TODO: Contributors should implement services for:
- Farmer verification processes
- Product catalog management
- Order processing and tracking
- Search and filtering operations
- Notification services

"""

# TODO: Import schemas as they are implemented
# from .farmer import FarmerCreate, FarmerResponse
# from .product import ProductCreate, ProductResponse

from .auth_service import auth_service

__all__: list[str] = [
    # TODO: Add service exports as they are implemented
    "auth_service",
]
