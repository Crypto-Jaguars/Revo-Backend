"""
Notification REST API endpoints for Farmers Marketplace.

Provides endpoints for managing notifications, preferences, and real-time updates.
"""

from typing import List, Optional
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.shared.notification import (
    Notification,
    NotificationCategory,
    NotificationStatus,
    NotificationType,
)
from app.models.users.user import User
from app.schemas.notification import (
    DeviceTokenCreate,
    DeviceTokenResponse,
    NotificationBulkCreate,
    NotificationCreate,
    NotificationListResponse,
    NotificationMarkReadRequest,
    NotificationPreferencesResponse,
    NotificationPreferencesUpdate,
    NotificationResponse,
    NotificationStatsResponse,
    NotificationTemplateCreate,
    NotificationTemplateResponse,
    NotificationTemplateUpdate,
    WebSocketNotification,
)
from app.services.auth_service import auth_service
from app.services.notification_service import notification_service

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


# Dependency to get current user
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Get current authenticated user."""
    return await auth_service.get_current_user_from_token(db, token)


# WebSocket connection manager for real-time notifications
class ConnectionManager:
    """Manages WebSocket connections for real-time notifications."""
    
    def __init__(self):
        self.active_connections: dict[uuid.UUID, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, user_id: uuid.UUID):
        """Connect a user's WebSocket."""
        await websocket.accept()
        self.active_connections[user_id] = websocket
    
    def disconnect(self, user_id: uuid.UUID):
        """Disconnect a user's WebSocket."""
        if user_id in self.active_connections:
            del self.active_connections[user_id]
    
    async def send_personal_message(self, message: dict, user_id: uuid.UUID):
        """Send message to specific user."""
        if user_id in self.active_connections:
            try:
                await self.active_connections[user_id].send_json(message)
            except:
                # Connection is dead, remove it
                self.disconnect(user_id)


manager = ConnectionManager()


# Notification CRUD endpoints

@router.post("/", response_model=NotificationResponse, status_code=status.HTTP_201_CREATED)
async def create_notification(
    notification_data: NotificationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new notification."""
    try:
        notification = await notification_service.send_notification(
            db=db,
            user_id=notification_data.user_id,
            notification_type=notification_data.notification_type,
            category=notification_data.category,
            title=notification_data.title,
            message=notification_data.message,
            template_name=notification_data.template_name,
            template_data=notification_data.template_data,
            data=notification_data.data,
            recipient_override=notification_data.recipient_override
        )
        
        # Send real-time notification if it's in-app
        if notification.notification_type == NotificationType.IN_APP:
            unread_count = await notification_service.get_unread_count(db, notification.user_id)
            await manager.send_personal_message(
                WebSocketNotification(
                    notification=NotificationResponse.model_validate(notification),
                    unread_count=unread_count
                ).model_dump(),
                notification.user_id
            )
        
        return NotificationResponse.model_validate(notification)
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create notification: {str(e)}"
        )


@router.post("/bulk", response_model=List[NotificationResponse])
async def create_bulk_notifications(
    notification_data: NotificationBulkCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create notifications for multiple users."""
    try:
        notifications = await notification_service.send_bulk_notification(
            db=db,
            user_ids=notification_data.user_ids,
            notification_type=notification_data.notification_type,
            category=notification_data.category,
            title=notification_data.title,
            message=notification_data.message,
            template_name=notification_data.template_name,
            template_data=notification_data.template_data,
            data=notification_data.data
        )
        
        # Send real-time notifications for in-app notifications
        if notification_data.notification_type == NotificationType.IN_APP:
            for notification in notifications:
                unread_count = await notification_service.get_unread_count(db, notification.user_id)
                await manager.send_personal_message(
                    WebSocketNotification(
                        notification=NotificationResponse.model_validate(notification),
                        unread_count=unread_count
                    ).model_dump(),
                    notification.user_id
                )
        
        return [NotificationResponse.model_validate(n) for n in notifications]
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create bulk notifications: {str(e)}"
        )


@router.get("/", response_model=NotificationListResponse)
async def get_notifications(
    notification_type: Optional[NotificationType] = Query(None),
    category: Optional[NotificationCategory] = Query(None),
    unread_only: bool = Query(False),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user's notifications with pagination."""
    offset = (page - 1) * per_page
    
    notifications = await notification_service.get_user_notifications(
        db=db,
        user_id=current_user.id,
        notification_type=notification_type,
        category=category,
        unread_only=unread_only,
        limit=per_page,
        offset=offset
    )
    
    # Get total count
    query = select(func.count(Notification.id)).where(Notification.user_id == current_user.id)
    
    if notification_type:
        query = query.where(Notification.notification_type == notification_type)
    if category:
        query = query.where(Notification.category == category)
    if unread_only:
        query = query.where(Notification.status != NotificationStatus.READ)
    
    result = await db.execute(query)
    total = result.scalar() or 0
    
    return NotificationListResponse(
        notifications=[NotificationResponse.model_validate(n) for n in notifications],
        total=total,
        page=page,
        per_page=per_page,
        has_next=offset + per_page < total,
        has_prev=page > 1
    )


@router.get("/unread-count", response_model=dict)
async def get_unread_count(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get count of unread notifications."""
    count = await notification_service.get_unread_count(db, current_user.id)
    return {"unread_count": count}


@router.get("/stats", response_model=NotificationStatsResponse)
async def get_notification_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get notification statistics for the user."""
    # Total notifications
    total_result = await db.execute(
        select(func.count(Notification.id))
        .where(Notification.user_id == current_user.id)
    )
    total_notifications = total_result.scalar() or 0
    
    # Unread count
    unread_count = await notification_service.get_unread_count(db, current_user.id)
    
    # By type
    type_result = await db.execute(
        select(Notification.notification_type, func.count(Notification.id))
        .where(Notification.user_id == current_user.id)
        .group_by(Notification.notification_type)
    )
    by_type = {row[0]: row[1] for row in type_result.fetchall()}
    
    # By category
    category_result = await db.execute(
        select(Notification.category, func.count(Notification.id))
        .where(Notification.user_id == current_user.id)
        .group_by(Notification.category)
    )
    by_category = {row[0]: row[1] for row in category_result.fetchall()}
    
    # By status
    status_result = await db.execute(
        select(Notification.status, func.count(Notification.id))
        .where(Notification.user_id == current_user.id)
        .group_by(Notification.status)
    )
    by_status = {row[0]: row[1] for row in status_result.fetchall()}
    
    return NotificationStatsResponse(
        total_notifications=total_notifications,
        unread_count=unread_count,
        by_type=by_type,
        by_category=by_category,
        by_status=by_status
    )


@router.patch("/mark-read", response_model=dict)
async def mark_notifications_read(
    request: NotificationMarkReadRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mark notifications as read."""
    marked_count = 0
    
    for notification_id in request.notification_ids:
        success = await notification_service.mark_as_read(
            db, notification_id, current_user.id
        )
        if success:
            marked_count += 1
    
    # Send updated unread count via WebSocket
    unread_count = await notification_service.get_unread_count(db, current_user.id)
    await manager.send_personal_message(
        {"type": "unread_count_update", "unread_count": unread_count},
        current_user.id
    )
    
    return {
        "marked_count": marked_count,
        "unread_count": unread_count
    }


@router.delete("/{notification_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_notification(
    notification_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a notification."""
    result = await db.execute(
        select(Notification)
        .where(
            Notification.id == notification_id,
            Notification.user_id == current_user.id
        )
    )
    notification = result.scalar_one_or_none()
    
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    
    await db.delete(notification)
    await db.commit()


# User preferences endpoints

@router.get("/preferences", response_model=NotificationPreferencesResponse)
async def get_notification_preferences(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user's notification preferences."""
    if not current_user.notification_preferences:
        # Create default preferences
        preferences = await notification_service.update_user_preferences(
            db, current_user.id, {}
        )
    else:
        preferences = current_user.notification_preferences
    
    return NotificationPreferencesResponse.model_validate(preferences)


@router.put("/preferences", response_model=NotificationPreferencesResponse)
async def update_notification_preferences(
    preferences_update: NotificationPreferencesUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update user's notification preferences."""
    preferences = await notification_service.update_user_preferences(
        db, current_user.id, preferences_update.model_dump(exclude_unset=True)
    )
    return NotificationPreferencesResponse.model_validate(preferences)


# Device token endpoints

@router.post("/device-tokens", response_model=DeviceTokenResponse)
async def register_device_token(
    device_token_data: DeviceTokenCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Register a device token for push notifications."""
    device_token = await notification_service.register_device_token(
        db, current_user.id, device_token_data.token, device_token_data.platform
    )
    return DeviceTokenResponse.model_validate(device_token)


@router.get("/device-tokens", response_model=List[DeviceTokenResponse])
async def get_device_tokens(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user's registered device tokens."""
    return [DeviceTokenResponse.model_validate(token) for token in current_user.device_tokens]


@router.delete("/device-tokens/{token_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_device_token(
    token_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a device token."""
    from app.models.shared.notification import DeviceToken
    
    result = await db.execute(
        select(DeviceToken)
        .where(
            DeviceToken.id == token_id,
            DeviceToken.user_id == current_user.id
        )
    )
    device_token = result.scalar_one_or_none()
    
    if not device_token:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device token not found"
        )
    
    await db.delete(device_token)
    await db.commit()


# Admin endpoints for templates (require admin role)

@router.post("/templates", response_model=NotificationTemplateResponse)
async def create_notification_template(
    template_data: NotificationTemplateCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a notification template (admin only)."""
    # TODO: Add admin role check
    from app.models.shared.notification import NotificationTemplate
    
    template = NotificationTemplate(**template_data.model_dump())
    db.add(template)
    await db.commit()
    await db.refresh(template)
    
    return NotificationTemplateResponse.model_validate(template)


@router.get("/templates", response_model=List[NotificationTemplateResponse])
async def get_notification_templates(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all notification templates (admin only)."""
    # TODO: Add admin role check
    from app.models.shared.notification import NotificationTemplate
    
    result = await db.execute(select(NotificationTemplate))
    templates = result.scalars().all()
    
    return [NotificationTemplateResponse.model_validate(t) for t in templates]


@router.put("/templates/{template_id}", response_model=NotificationTemplateResponse)
async def update_notification_template(
    template_id: int,
    template_update: NotificationTemplateUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a notification template (admin only)."""
    # TODO: Add admin role check
    from app.models.shared.notification import NotificationTemplate
    
    result = await db.execute(
        select(NotificationTemplate).where(NotificationTemplate.id == template_id)
    )
    template = result.scalar_one_or_none()
    
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )
    
    update_data = template_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(template, field, value)
    
    await db.commit()
    await db.refresh(template)
    
    return NotificationTemplateResponse.model_validate(template)


# WebSocket endpoint for real-time notifications

@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str = Query(...),
    db: AsyncSession = Depends(get_db)
):
    """WebSocket endpoint for real-time notifications."""
    try:
        # Authenticate user from token
        user = await auth_service.get_current_user_from_token(db, token)
        
        # Connect WebSocket
        await manager.connect(websocket, user.id)
        
        # Send current unread count
        unread_count = await notification_service.get_unread_count(db, user.id)
        await websocket.send_json({
            "type": "unread_count_update",
            "unread_count": unread_count
        })
        
        # Keep connection alive
        while True:
            # Wait for messages (ping/pong to keep alive)
            try:
                data = await websocket.receive_text()
                if data == "ping":
                    await websocket.send_text("pong")
            except WebSocketDisconnect:
                break
    
    except Exception as e:
        await websocket.close(code=1008, reason=str(e))
    finally:
        if 'user' in locals():
            manager.disconnect(user.id)
