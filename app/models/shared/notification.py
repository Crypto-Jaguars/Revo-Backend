"""
Notification models for the Farmers Marketplace.

Supports email, push, and in-app notifications with templates and user preferences.
"""

from datetime import datetime
from enum import Enum
from typing import Dict, Optional

from sqlalchemy import JSON, Boolean, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid

from app.models.base import BaseModel


class NotificationType(str, Enum):
    """Types of notifications supported."""
    
    EMAIL = "email"
    PUSH = "push"
    IN_APP = "in_app"


class NotificationCategory(str, Enum):
    """Categories of notifications."""
    
    ORDER = "order"
    PRODUCT = "product"
    ACCOUNT = "account"
    MARKETING = "marketing"
    SYSTEM = "system"


class NotificationStatus(str, Enum):
    """Status of notification delivery."""
    
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    READ = "read"


class NotificationTemplate(BaseModel):
    """Template for notifications."""
    
    __tablename__ = "notification_templates"
    
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    category: Mapped[NotificationCategory] = mapped_column(String(50))
    notification_type: Mapped[NotificationType] = mapped_column(String(20))
    
    # Template content
    subject_template: Mapped[Optional[str]] = mapped_column(String(200))
    body_template: Mapped[str] = mapped_column(Text)
    
    # Metadata
    variables: Mapped[Optional[Dict]] = mapped_column(JSON)  # Expected template variables
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Relationships
    notifications: Mapped[list["Notification"]] = relationship(
        "Notification", back_populates="template"
    )


class Notification(BaseModel):
    """Individual notification record."""
    
    __tablename__ = "notifications"
    
    # Basic info
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), index=True)
    template_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("notification_templates.id")
    )
    
    # Notification details
    notification_type: Mapped[NotificationType] = mapped_column(String(20))
    category: Mapped[NotificationCategory] = mapped_column(String(50))
    status: Mapped[NotificationStatus] = mapped_column(
        String(20), default=NotificationStatus.PENDING
    )
    
    # Content
    title: Mapped[str] = mapped_column(String(200))
    message: Mapped[str] = mapped_column(Text)
    data: Mapped[Optional[Dict]] = mapped_column(JSON)  # Additional data payload
    
    # Delivery details
    recipient: Mapped[str] = mapped_column(String(255))  # Email, device token, etc.
    sent_at: Mapped[Optional[datetime]] = mapped_column()
    delivered_at: Mapped[Optional[datetime]] = mapped_column()
    read_at: Mapped[Optional[datetime]] = mapped_column()
    
    # Error handling
    error_message: Mapped[Optional[str]] = mapped_column(Text)
    retry_count: Mapped[int] = mapped_column(default=0)
    
    # Relationships
    template: Mapped[Optional[NotificationTemplate]] = relationship(
        "NotificationTemplate", back_populates="notifications"
    )
    user: Mapped["User"] = relationship("User", back_populates="notifications")


class UserNotificationPreference(BaseModel):
    """User preferences for notifications."""
    
    __tablename__ = "user_notification_preferences"
    
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id"), unique=True, index=True
    )
    
    # Email preferences
    email_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    email_orders: Mapped[bool] = mapped_column(Boolean, default=True)
    email_products: Mapped[bool] = mapped_column(Boolean, default=True)
    email_account: Mapped[bool] = mapped_column(Boolean, default=True)
    email_marketing: Mapped[bool] = mapped_column(Boolean, default=False)
    email_system: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Push preferences
    push_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    push_orders: Mapped[bool] = mapped_column(Boolean, default=True)
    push_products: Mapped[bool] = mapped_column(Boolean, default=False)
    push_account: Mapped[bool] = mapped_column(Boolean, default=True)
    push_marketing: Mapped[bool] = mapped_column(Boolean, default=False)
    push_system: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # In-app preferences
    in_app_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    in_app_orders: Mapped[bool] = mapped_column(Boolean, default=True)
    in_app_products: Mapped[bool] = mapped_column(Boolean, default=True)
    in_app_account: Mapped[bool] = mapped_column(Boolean, default=True)
    in_app_marketing: Mapped[bool] = mapped_column(Boolean, default=False)
    in_app_system: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Quiet hours
    quiet_hours_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    quiet_hours_start: Mapped[Optional[str]] = mapped_column(String(5))  # "22:00"
    quiet_hours_end: Mapped[Optional[str]] = mapped_column(String(5))    # "08:00"
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="notification_preferences")


class DeviceToken(BaseModel):
    """Device tokens for push notifications."""
    
    __tablename__ = "device_tokens"
    
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), index=True)
    token: Mapped[str] = mapped_column(String(500), unique=True, index=True)
    platform: Mapped[str] = mapped_column(String(20))  # "ios", "android", "web"
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="device_tokens")
