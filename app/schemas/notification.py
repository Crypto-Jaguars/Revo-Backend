"""
Pydantic schemas for notification system.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
import uuid

from pydantic import BaseModel, Field

from app.models.shared.notification import (
    NotificationCategory,
    NotificationStatus,
    NotificationType,
)


class NotificationBase(BaseModel):
    """Base notification schema."""
    
    title: str = Field(..., max_length=200)
    message: str
    category: NotificationCategory
    data: Optional[Dict[str, Any]] = None


class NotificationCreate(NotificationBase):
    """Schema for creating notifications."""
    
    user_id: uuid.UUID
    notification_type: NotificationType
    template_name: Optional[str] = None
    template_data: Optional[Dict[str, Any]] = None
    recipient_override: Optional[str] = None


class NotificationBulkCreate(BaseModel):
    """Schema for creating bulk notifications."""
    
    user_ids: List[uuid.UUID]
    notification_type: NotificationType
    title: str = Field(..., max_length=200)
    message: str
    category: NotificationCategory
    template_name: Optional[str] = None
    template_data: Optional[Dict[str, Any]] = None
    data: Optional[Dict[str, Any]] = None


class NotificationResponse(NotificationBase):
    """Schema for notification responses."""
    
    id: int
    user_id: uuid.UUID
    notification_type: NotificationType
    status: NotificationStatus
    recipient: str
    created_at: datetime
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    read_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class NotificationListResponse(BaseModel):
    """Schema for paginated notification list."""
    
    notifications: List[NotificationResponse]
    total: int
    page: int
    per_page: int
    has_next: bool
    has_prev: bool


class NotificationMarkReadRequest(BaseModel):
    """Schema for marking notifications as read."""
    
    notification_ids: List[int]


class NotificationPreferencesBase(BaseModel):
    """Base notification preferences schema."""
    
    # Email preferences
    email_enabled: bool = True
    email_orders: bool = True
    email_products: bool = True
    email_account: bool = True
    email_marketing: bool = False
    email_system: bool = True
    
    # Push preferences
    push_enabled: bool = True
    push_orders: bool = True
    push_products: bool = False
    push_account: bool = True
    push_marketing: bool = False
    push_system: bool = True
    
    # In-app preferences
    in_app_enabled: bool = True
    in_app_orders: bool = True
    in_app_products: bool = True
    in_app_account: bool = True
    in_app_marketing: bool = False
    in_app_system: bool = True
    
    # Quiet hours
    quiet_hours_enabled: bool = False
    quiet_hours_start: Optional[str] = Field(None, pattern=r"^([01]?[0-9]|2[0-3]):[0-5][0-9]$")
    quiet_hours_end: Optional[str] = Field(None, pattern=r"^([01]?[0-9]|2[0-3]):[0-5][0-9]$")


class NotificationPreferencesUpdate(NotificationPreferencesBase):
    """Schema for updating notification preferences."""
    pass


class NotificationPreferencesResponse(NotificationPreferencesBase):
    """Schema for notification preferences response."""
    
    id: int
    user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class DeviceTokenCreate(BaseModel):
    """Schema for registering device tokens."""
    
    token: str = Field(..., max_length=500)
    platform: str = Field(..., pattern=r"^(ios|android|web)$")


class DeviceTokenResponse(BaseModel):
    """Schema for device token response."""
    
    id: int
    user_id: uuid.UUID
    token: str
    platform: str
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class NotificationTemplateBase(BaseModel):
    """Base notification template schema."""
    
    name: str = Field(..., max_length=100)
    category: NotificationCategory
    notification_type: NotificationType
    subject_template: Optional[str] = Field(None, max_length=200)
    body_template: str
    variables: Optional[Dict[str, Any]] = None
    is_active: bool = True


class NotificationTemplateCreate(NotificationTemplateBase):
    """Schema for creating notification templates."""
    pass


class NotificationTemplateUpdate(BaseModel):
    """Schema for updating notification templates."""
    
    subject_template: Optional[str] = Field(None, max_length=200)
    body_template: Optional[str] = None
    variables: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class NotificationTemplateResponse(NotificationTemplateBase):
    """Schema for notification template response."""
    
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class NotificationStatsResponse(BaseModel):
    """Schema for notification statistics."""
    
    total_notifications: int
    unread_count: int
    by_type: Dict[str, int]
    by_category: Dict[str, int]
    by_status: Dict[str, int]


class WebSocketNotification(BaseModel):
    """Schema for real-time WebSocket notifications."""
    
    type: str = "notification"
    notification: NotificationResponse
    unread_count: int
