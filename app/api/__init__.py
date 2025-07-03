"""
REST API endpoints for Farmers Marketplace.

TODO: Contributors should implement REST endpoints for:
- Health checks and monitoring
- Mobile app optimized endpoints
- File upload endpoints for product images
- Webhook endpoints for external integrations

"""

# TODO: Import API routers as they are implemented
# from .health import router as health_router
# from .mobile import router as mobile_router
from .users import router as users_router

__all__ = [
    "users_router",
    # TODO: Add API router exports as they are implemented
]
