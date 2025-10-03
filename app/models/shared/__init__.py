"""
Shared models used across the marketplace.

TODO: Contributors should implement:
- Location for geographic coordinates and addresses ✅
- Review for farmer and product ratings
- Notification for system notifications ✅
- Media for handling product images and farm photos

"""

from .location import Location
from .notification import (
    Notification,
    NotificationTemplate,
    UserNotificationPreference,
    DeviceToken,
    NotificationType,
    NotificationCategory,
    NotificationStatus,
)

from typing import List

__all__: List[str] = [
    "Location",
    "Notification",
    "NotificationTemplate", 
    "UserNotificationPreference",
    "DeviceToken",
    "NotificationType",
    "NotificationCategory",
    "NotificationStatus",
]
