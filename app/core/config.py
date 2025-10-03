"""
Application settings using Pydantic.
"""

from functools import lru_cache
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    # Environment
    environment: str = "development"
    debug: bool = True

    # Database
    postgres_host: str = Field(default="localhost")
    postgres_port: int = Field(default=5432)
    postgres_user: str = Field(default="myuser")
    postgres_password: str = Field(default="mypassword")
    postgres_db: str = Field(default="mydatabase")
    database_url: str = Field(
        default="postgresql+asyncpg://myuser:mypassword@localhost:5432/mydatabase"
    )

    # Security
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # CORS
    allowed_origins: List[str] = ["http://localhost:3000", "http://localhost:8000"]

    # GraphQL
    graphql_debug: bool = Field(default=True)
    
    # Email Configuration
    smtp_server: str = Field(default="smtp.gmail.com")
    smtp_port: int = Field(default=587)
    smtp_username: str = Field(default="")
    smtp_password: str = Field(default="")
    from_email: str = Field(default="noreply@farmersmarketplace.com")
    
    # Push Notification Configuration
    fcm_server_key: str = Field(default="")  # Firebase Cloud Messaging
    apns_key_id: str = Field(default="")     # Apple Push Notification Service
    apns_team_id: str = Field(default="")
    apns_bundle_id: str = Field(default="com.farmersmarketplace.app")
    
    # Notification Settings
    notification_retry_attempts: int = Field(default=3)
    notification_retry_delay: int = Field(default=300)  # seconds
    max_bulk_notifications: int = Field(default=1000)

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
    )

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
