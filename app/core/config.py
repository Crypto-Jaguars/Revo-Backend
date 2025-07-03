"""
Application settings using Pydantic.
"""

from functools import lru_cache
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    # Environmen
    environment: str = "development"
    debug: bool = True

    # Database
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_user: str = "myuser"
    postgres_password: str = "mypassword"
    postgres_db: str = "mydatabase"
    database_url: str = (
        "postgresql+asyncpg://myuser:mypassword@localhost:5432/mydatabase"
    )

    # Security
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # CORS
    allowed_origins: List[str] = ["http://localhost:3000", "http://localhost:8000"]

    # GraphQL
    graphql_debug: bool = Field(default=True)

    class Config:
        env_file = ".env"
        case_sensitive = False

    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.environment == "development"

    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.environment == "production"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
