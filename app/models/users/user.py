"""
User model for authentication.
"""

import enum
import uuid
from typing import TYPE_CHECKING

from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, String, func, Enum as SQLAlchemyEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.models.base import Base
from enum import Enum

if TYPE_CHECKING:
    from app.models.farmers.farmer import Farmer

class UserType(Enum):
    """User type enumeration."""
    FARMER = "FARMER"
    BUYER = "BUYER"
    ADMIN = "ADMIN"

class User(Base):
    """User model for authentication and user management."""
    
    __tablename__ = "users"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    user_type: Mapped[UserType] = mapped_column(SQLAlchemyEnum(UserType), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
    
    # Relationships
    farmer: Mapped["Farmer"] = relationship("Farmer", back_populates="user", uselist=False)
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, email='{self.email}', user_type='{self.user_type}')>"

