"""
FastAPI application for Farmers Marketplace - TEMPLATE.

This is a basic setup that provides the foundation for the marketplace.

TODO: Expand this application with:
- Authentication middleware
- Complete API endpoints
- Error handlers
- Rate limiting
- CORS configuration
- Logging setup
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from app.api.auth import router as auth_router
from app.api.users import router as users_router
from app.api.farmers import router as farmers_router
from app.api.notifications import router as notifications_router
from app.core.config import get_settings
from app.core.database import init_db
from app.graphql.schema import graphql_router
# from app.core.middleware import AuthenticationMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    logger.info("Starting up...")
    await init_db()
    logger.info("Database initialized")
    yield
    logger.info("Shutting down...")


# Initialize FastAPI application
settings = get_settings()
app = FastAPI(
    title="Farmers Marketplace API",
    description="Backend API for connecting agricultural producers with consumers",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Optional: Add authentication middleware for automatic route protection
# Uncomment the lines below to enable automatic authentication for protected paths
# app.add_middleware(
#     AuthenticationMiddleware,
#     protected_paths=["/api/v1/protected", "/api/v1/admin"],
#     public_paths=["/", "/docs", "/redoc", "/auth/login", "/auth/register"],
#     require_auth_by_default=False
# )

# Include GraphQL router
app.include_router(graphql_router, prefix="/graphql", tags=["graphql"])

# Include API routers
app.include_router(auth_router, prefix="/auth", tags=["authentication"])
app.include_router(users_router, prefix="/api/users", tags=["users"])
app.include_router(farmers_router, prefix="/api/farmers", tags=["farmers"])
app.include_router(notifications_router, prefix="/api/notifications", tags=["notifications"])


# Basic root endpoint
@app.get("/", tags=["root"])
async def root():
    """Root endpoint."""
    return {
        "message": "🌾 Farmers Marketplace API",
        "description": "Connecting agricultural producers with consumers",
        "docs": "/docs",
        "graphql": "/graphql",
        "status": "ready_for_contributors",
    }


# TODO: Contributors should add additional routers and middleware:
# app.include_router(api_router, prefix="/api/v1", tags=["api"])
# app.include_router(mobile_router, prefix="/mobile", tags=["mobile"])

# TODO: Add exception handlers, middleware, and additional configuration
# See CONTRIBUTING.md for specific implementation tasks
