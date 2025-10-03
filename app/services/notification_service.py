"""
Comprehensive notification service for the Farmers Marketplace.

Handles email, push, and in-app notifications with templates, preferences, and async delivery.
"""

import asyncio
import json
import smtplib
from datetime import datetime, time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any, Dict, List, Optional, Union
import uuid

import aiohttp
from fastapi import HTTPException, status
from jinja2 import Template
from loguru import logger
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.models.shared.notification import (
    DeviceToken,
    Notification,
    NotificationCategory,
    NotificationStatus,
    NotificationTemplate,
    NotificationType,
    UserNotificationPreference,
)
from app.models.users.user import User


class EmailProvider:
    """Email service provider for sending notifications."""
    
    def __init__(self, settings):
        self.settings = settings
        self.smtp_server = getattr(settings, 'smtp_server', 'smtp.gmail.com')
        self.smtp_port = getattr(settings, 'smtp_port', 587)
        self.smtp_username = getattr(settings, 'smtp_username', '')
        self.smtp_password = getattr(settings, 'smtp_password', '')
        self.from_email = getattr(settings, 'from_email', 'noreply@farmersmarketplace.com')
    
    async def send_email(self, to_email: str, subject: str, body: str) -> bool:
        """Send email using SMTP."""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.from_email
            msg['To'] = to_email
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'html'))
            
            # Use asyncio to run SMTP in thread pool
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None, self._send_smtp_email, msg, to_email
            )
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return False
    
    def _send_smtp_email(self, msg: MIMEMultipart, to_email: str):
        """Send SMTP email in thread."""
        with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
            server.starttls()
            if self.smtp_username and self.smtp_password:
                server.login(self.smtp_username, self.smtp_password)
            server.send_message(msg, to_addrs=[to_email])


class PushProvider:
    """Push notification service provider."""
    
    def __init__(self, settings):
        self.settings = settings
        self.fcm_server_key = getattr(settings, 'fcm_server_key', '')
        self.apns_key_id = getattr(settings, 'apns_key_id', '')
        self.apns_team_id = getattr(settings, 'apns_team_id', '')
        self.apns_bundle_id = getattr(settings, 'apns_bundle_id', '')
    
    async def send_push_notification(
        self, 
        device_token: str, 
        platform: str, 
        title: str, 
        body: str, 
        data: Optional[Dict] = None
    ) -> bool:
        """Send push notification based on platform."""
        try:
            if platform.lower() == 'android':
                return await self._send_fcm_notification(device_token, title, body, data)
            elif platform.lower() == 'ios':
                return await self._send_apns_notification(device_token, title, body, data)
            elif platform.lower() == 'web':
                return await self._send_web_push_notification(device_token, title, body, data)
            else:
                logger.warning(f"Unsupported platform: {platform}")
                return False
        except Exception as e:
            logger.error(f"Failed to send push notification: {str(e)}")
            return False
    
    async def _send_fcm_notification(
        self, token: str, title: str, body: str, data: Optional[Dict] = None
    ) -> bool:
        """Send FCM notification for Android."""
        if not self.fcm_server_key:
            logger.warning("FCM server key not configured")
            return False
        
        url = "https://fcm.googleapis.com/fcm/send"
        headers = {
            "Authorization": f"key={self.fcm_server_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "to": token,
            "notification": {
                "title": title,
                "body": body
            },
            "data": data or {}
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as response:
                return response.status == 200
    
    async def _send_apns_notification(
        self, token: str, title: str, body: str, data: Optional[Dict] = None
    ) -> bool:
        """Send APNS notification for iOS."""
        # This would require PyJWT and cryptography for proper APNS implementation
        logger.info(f"APNS notification would be sent to {token}: {title}")
        return True  # Placeholder
    
    async def _send_web_push_notification(
        self, token: str, title: str, body: str, data: Optional[Dict] = None
    ) -> bool:
        """Send web push notification."""
        # This would require pywebpush library for proper web push implementation
        logger.info(f"Web push notification would be sent to {token}: {title}")
        return True  # Placeholder


class NotificationService:
    """Main notification service handling all notification types."""
    
    def __init__(self):
        self.settings = get_settings()
        self.email_provider = EmailProvider(self.settings)
        self.push_provider = PushProvider(self.settings)
    
    async def send_notification(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        notification_type: NotificationType,
        category: NotificationCategory,
        title: str,
        message: str,
        template_name: Optional[str] = None,
        template_data: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        recipient_override: Optional[str] = None
    ) -> Notification:
        """Send a notification to a user."""
        
        # Get user and preferences
        user = await self._get_user_with_preferences(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Check if user wants this type of notification
        if not await self._should_send_notification(user, notification_type, category):
            logger.info(f"Notification blocked by user preferences: {user_id}")
            return None
        
        # Check quiet hours
        if await self._is_quiet_hours(user):
            logger.info(f"Notification delayed due to quiet hours: {user_id}")
            # Could implement delayed sending here
        
        # Get template if specified
        template = None
        if template_name:
            template = await self._get_template(db, template_name)
            if template and template_data:
                title, message = await self._render_template(template, template_data)
        
        # Create notification record
        notification = Notification(
            user_id=user_id,
            template_id=template.id if template else None,
            notification_type=notification_type,
            category=category,
            status=NotificationStatus.PENDING,
            title=title,
            message=message,
            data=data,
            recipient=recipient_override or await self._get_recipient(user, notification_type)
        )
        
        db.add(notification)
        await db.commit()
        await db.refresh(notification)
        
        # Send notification asynchronously
        asyncio.create_task(
            self._deliver_notification(db, notification)
        )
        
        return notification
    
    async def send_bulk_notification(
        self,
        db: AsyncSession,
        user_ids: List[uuid.UUID],
        notification_type: NotificationType,
        category: NotificationCategory,
        title: str,
        message: str,
        template_name: Optional[str] = None,
        template_data: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None
    ) -> List[Notification]:
        """Send notifications to multiple users."""
        notifications = []
        
        for user_id in user_ids:
            try:
                notification = await self.send_notification(
                    db, user_id, notification_type, category, title, message,
                    template_name, template_data, data
                )
                if notification:
                    notifications.append(notification)
            except Exception as e:
                logger.error(f"Failed to send notification to user {user_id}: {str(e)}")
        
        return notifications
    
    async def mark_as_read(
        self, 
        db: AsyncSession, 
        notification_id: int, 
        user_id: uuid.UUID
    ) -> bool:
        """Mark notification as read."""
        result = await db.execute(
            update(Notification)
            .where(
                Notification.id == notification_id,
                Notification.user_id == user_id
            )
            .values(
                status=NotificationStatus.READ,
                read_at=datetime.utcnow()
            )
        )
        await db.commit()
        return result.rowcount > 0
    
    async def get_user_notifications(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        notification_type: Optional[NotificationType] = None,
        category: Optional[NotificationCategory] = None,
        unread_only: bool = False,
        limit: int = 50,
        offset: int = 0
    ) -> List[Notification]:
        """Get notifications for a user."""
        query = select(Notification).where(Notification.user_id == user_id)
        
        if notification_type:
            query = query.where(Notification.notification_type == notification_type)
        
        if category:
            query = query.where(Notification.category == category)
        
        if unread_only:
            query = query.where(Notification.status != NotificationStatus.READ)
        
        query = query.order_by(Notification.created_at.desc())
        query = query.offset(offset).limit(limit)
        
        result = await db.execute(query)
        return result.scalars().all()
    
    async def get_unread_count(
        self, 
        db: AsyncSession, 
        user_id: uuid.UUID
    ) -> int:
        """Get count of unread notifications."""
        from sqlalchemy import func
        
        result = await db.execute(
            select(func.count(Notification.id))
            .where(
                Notification.user_id == user_id,
                Notification.notification_type == NotificationType.IN_APP,
                Notification.status != NotificationStatus.READ
            )
        )
        return result.scalar() or 0
    
    async def update_user_preferences(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        preferences: Dict[str, Any]
    ) -> UserNotificationPreference:
        """Update user notification preferences."""
        # Get or create preferences
        result = await db.execute(
            select(UserNotificationPreference)
            .where(UserNotificationPreference.user_id == user_id)
        )
        user_prefs = result.scalar_one_or_none()
        
        if not user_prefs:
            user_prefs = UserNotificationPreference(user_id=user_id)
            db.add(user_prefs)
        
        # Update preferences
        for key, value in preferences.items():
            if hasattr(user_prefs, key):
                setattr(user_prefs, key, value)
        
        await db.commit()
        await db.refresh(user_prefs)
        return user_prefs
    
    async def register_device_token(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        token: str,
        platform: str
    ) -> DeviceToken:
        """Register device token for push notifications."""
        # Deactivate existing tokens for this device
        await db.execute(
            update(DeviceToken)
            .where(DeviceToken.token == token)
            .values(is_active=False)
        )
        
        # Create new token
        device_token = DeviceToken(
            user_id=user_id,
            token=token,
            platform=platform.lower(),
            is_active=True
        )
        
        db.add(device_token)
        await db.commit()
        await db.refresh(device_token)
        return device_token
    
    # Private helper methods
    
    async def _get_user_with_preferences(
        self, db: AsyncSession, user_id: uuid.UUID
    ) -> Optional[User]:
        """Get user with notification preferences."""
        result = await db.execute(
            select(User)
            .where(User.id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def _should_send_notification(
        self, 
        user: User, 
        notification_type: NotificationType, 
        category: NotificationCategory
    ) -> bool:
        """Check if notification should be sent based on user preferences."""
        if not user.notification_preferences:
            return True  # Default to sending if no preferences set
        
        prefs = user.notification_preferences
        
        # Check global settings
        if notification_type == NotificationType.EMAIL and not prefs.email_enabled:
            return False
        elif notification_type == NotificationType.PUSH and not prefs.push_enabled:
            return False
        elif notification_type == NotificationType.IN_APP and not prefs.in_app_enabled:
            return False
        
        # Check category-specific settings
        category_attr = f"{notification_type.value}_{category.value}"
        if hasattr(prefs, category_attr):
            return getattr(prefs, category_attr)
        
        return True
    
    async def _is_quiet_hours(self, user: User) -> bool:
        """Check if current time is within user's quiet hours."""
        if not user.notification_preferences or not user.notification_preferences.quiet_hours_enabled:
            return False
        
        prefs = user.notification_preferences
        if not prefs.quiet_hours_start or not prefs.quiet_hours_end:
            return False
        
        now = datetime.now().time()
        start_time = time.fromisoformat(prefs.quiet_hours_start)
        end_time = time.fromisoformat(prefs.quiet_hours_end)
        
        if start_time <= end_time:
            return start_time <= now <= end_time
        else:  # Quiet hours span midnight
            return now >= start_time or now <= end_time
    
    async def _get_template(
        self, db: AsyncSession, template_name: str
    ) -> Optional[NotificationTemplate]:
        """Get notification template by name."""
        result = await db.execute(
            select(NotificationTemplate)
            .where(
                NotificationTemplate.name == template_name,
                NotificationTemplate.is_active == True
            )
        )
        return result.scalar_one_or_none()
    
    async def _render_template(
        self, 
        template: NotificationTemplate, 
        data: Dict[str, Any]
    ) -> tuple[str, str]:
        """Render notification template with data."""
        try:
            subject_template = Template(template.subject_template or "")
            body_template = Template(template.body_template)
            
            subject = subject_template.render(**data) if template.subject_template else ""
            body = body_template.render(**data)
            
            return subject, body
        except Exception as e:
            logger.error(f"Template rendering failed: {str(e)}")
            return "Notification", template.body_template
    
    async def _get_recipient(
        self, user: User, notification_type: NotificationType
    ) -> str:
        """Get recipient address based on notification type."""
        if notification_type == NotificationType.EMAIL:
            return user.email
        elif notification_type == NotificationType.IN_APP:
            return str(user.id)
        else:  # PUSH
            # Would need to get active device token
            return ""
    
    async def _deliver_notification(
        self, db: AsyncSession, notification: Notification
    ):
        """Deliver notification via appropriate channel."""
        try:
            success = False
            
            if notification.notification_type == NotificationType.EMAIL:
                success = await self.email_provider.send_email(
                    notification.recipient,
                    notification.title,
                    notification.message
                )
            
            elif notification.notification_type == NotificationType.PUSH:
                # Get user's device tokens
                result = await db.execute(
                    select(DeviceToken)
                    .where(
                        DeviceToken.user_id == notification.user_id,
                        DeviceToken.is_active == True
                    )
                )
                device_tokens = result.scalars().all()
                
                for device_token in device_tokens:
                    await self.push_provider.send_push_notification(
                        device_token.token,
                        device_token.platform,
                        notification.title,
                        notification.message,
                        notification.data
                    )
                success = len(device_tokens) > 0
            
            elif notification.notification_type == NotificationType.IN_APP:
                # In-app notifications are just stored in database
                success = True
            
            # Update notification status
            notification.status = NotificationStatus.SENT if success else NotificationStatus.FAILED
            notification.sent_at = datetime.utcnow()
            
            if not success:
                notification.retry_count += 1
                notification.error_message = "Delivery failed"
            
            await db.commit()
            
        except Exception as e:
            logger.error(f"Notification delivery failed: {str(e)}")
            notification.status = NotificationStatus.FAILED
            notification.error_message = str(e)
            notification.retry_count += 1
            await db.commit()


# Global service instance
notification_service = NotificationService()
