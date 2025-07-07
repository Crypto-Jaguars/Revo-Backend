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
from typing import Any, AsyncGenerator

from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.auth import router as auth_router
from app.core.config import get_settings
from app.core.database import init_db, get_db
from app.graphql.schema import schema
from strawberry.fastapi import GraphQLRouter


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
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
    description="Backend API for connecting agricultural producers with consumers",  # noqa: E501
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


async def get_context(
    request: Request, db: AsyncSession = Depends(get_db)
) -> dict[str, Any]:
    ctx = {"request": request, "db": db}
    return ctx


graphql_router: Any = GraphQLRouter(schema, context_getter=get_context)

app.include_router(graphql_router, prefix="/graphql", tags=["graphql"])
app.include_router(auth_router, prefix="/auth", tags=["authentication"])


# Basic root endpoint
@app.get("/", tags=["root"])
async def root() -> dict[str, str]:
    """Root endpoint."""
    return {
        "message": "🌾 Farmers Marketplace API",
        "description": "Connecting agricultural producers with consumers",
        "docs": "/docs",
        "graphql": "/graphql",
        "status": "ready_for_contributors",
    }


# TODO: Contributors should add additional routers and middleware:
# app.include_router(auth_router, prefix="/auth", tags=["authentication"])
# app.include_router(api_router, prefix="/api/v1", tags=["api"])
# app.include_router(mobile_router, prefix="/mobile", tags=["mobile"])

# TODO: Add exception handlers, middleware, and additional configuration
# See CONTRIBUTING.md for specific implementation tasks
