"""
Example usage of the notification system.

This file demonstrates how to use the notification service for common scenarios.
"""

import asyncio
import uuid
from datetime import datetime

from app.core.database import get_db
from app.models.shared.notification import NotificationCategory, NotificationType
from app.services.notification_service import notification_service


async def example_new_order_notifications():
    """Example: Send notifications for a new order."""
    print("📦 Example: New Order Notifications")
    
    async for db in get_db():
        try:
            # Sample data
            farmer_id = uuid.uuid4()  # Replace with actual farmer ID
            buyer_id = uuid.uuid4()   # Replace with actual buyer ID
            
            order_data = {
                "order_id": "ORD-2024-001",
                "farmer_name": "Green Valley Farm",
                "buyer_name": "John Smith",
                "total_amount": 45.50,
                "item_count": 3,
                "delivery_date": "2024-01-15",
                "dashboard_url": "https://farmersmarketplace.com/dashboard",
                "order_url": "https://farmersmarketplace.com/orders/ORD-2024-001"
            }
            
            # Send email notification to farmer
            farmer_notification = await notification_service.send_notification(
                db=db,
                user_id=farmer_id,
                notification_type=NotificationType.EMAIL,
                category=NotificationCategory.ORDER,
                title="New Order Received",
                message="You have a new order!",
                template_name="new_order_farmer",
                template_data=order_data
            )
            print(f"  ✅ Farmer email notification created: {farmer_notification.id}")
            
            # Send confirmation email to buyer
            buyer_notification = await notification_service.send_notification(
                db=db,
                user_id=buyer_id,
                notification_type=NotificationType.EMAIL,
                category=NotificationCategory.ORDER,
                title="Order Confirmed",
                message="Your order has been confirmed!",
                template_name="new_order_buyer",
                template_data=order_data
            )
            print(f"  ✅ Buyer email notification created: {buyer_notification.id}")
            
            # Send push notification to farmer
            push_notification = await notification_service.send_notification(
                db=db,
                user_id=farmer_id,
                notification_type=NotificationType.PUSH,
                category=NotificationCategory.ORDER,
                title="New Order!",
                message=f"Order #{order_data['order_id']} from {order_data['buyer_name']}"
            )
            print(f"  ✅ Farmer push notification created: {push_notification.id}")
            
        finally:
            await db.close()
        break


async def example_order_status_updates():
    """Example: Send order status update notifications."""
    print("\n📋 Example: Order Status Updates")
    
    async for db in get_db():
        try:
            buyer_id = uuid.uuid4()  # Replace with actual buyer ID
            
            status_updates = [
                {
                    "status_name": "Confirmed",
                    "status_message": "Your order has been confirmed and is being prepared."
                },
                {
                    "status_name": "Ready for Pickup",
                    "status_message": "Your order is ready! Please come to the pickup location."
                },
                {
                    "status_name": "Completed",
                    "status_message": "Thank you for your order! We hope you enjoyed your fresh produce."
                }
            ]
            
            for status in status_updates:
                notification = await notification_service.send_notification(
                    db=db,
                    user_id=buyer_id,
                    notification_type=NotificationType.PUSH,
                    category=NotificationCategory.ORDER,
                    title=f"Order Update: {status['status_name']}",
                    message=status['status_message'],
                    template_name="order_status_update",
                    template_data={
                        "order_id": "ORD-2024-001",
                        "farmer_name": "Green Valley Farm",
                        **status
                    }
                )
                print(f"  ✅ Status update notification: {status['status_name']}")
            
        finally:
            await db.close()
        break


async def example_product_notifications():
    """Example: Send product-related notifications."""
    print("\n🥕 Example: Product Notifications")
    
    async for db in get_db():
        try:
            farmer_id = uuid.uuid4()  # Replace with actual farmer ID
            
            # Low stock alert
            low_stock_notification = await notification_service.send_notification(
                db=db,
                user_id=farmer_id,
                notification_type=NotificationType.IN_APP,
                category=NotificationCategory.PRODUCT,
                title="Low Stock Alert",
                message="Your product is running low on stock",
                template_name="product_low_stock",
                template_data={
                    "product_name": "Organic Tomatoes",
                    "current_stock": 5
                }
            )
            print(f"  ✅ Low stock notification created: {low_stock_notification.id}")
            
            # Product approved notification
            approved_notification = await notification_service.send_notification(
                db=db,
                user_id=farmer_id,
                notification_type=NotificationType.EMAIL,
                category=NotificationCategory.PRODUCT,
                title="Product Approved",
                message="Your product has been approved!",
                template_name="new_product_approved",
                template_data={
                    "farmer_name": "Green Valley Farm",
                    "product_name": "Organic Carrots",
                    "product_url": "https://farmersmarketplace.com/products/organic-carrots"
                }
            )
            print(f"  ✅ Product approved notification created: {approved_notification.id}")
            
        finally:
            await db.close()
        break


async def example_welcome_notifications():
    """Example: Send welcome notifications for new users."""
    print("\n👋 Example: Welcome Notifications")
    
    async for db in get_db():
        try:
            farmer_id = uuid.uuid4()  # Replace with actual farmer ID
            buyer_id = uuid.uuid4()   # Replace with actual buyer ID
            
            # Welcome farmer
            farmer_welcome = await notification_service.send_notification(
                db=db,
                user_id=farmer_id,
                notification_type=NotificationType.EMAIL,
                category=NotificationCategory.ACCOUNT,
                title="Welcome to Farmers Marketplace!",
                message="Welcome to our farming community!",
                template_name="welcome_farmer",
                template_data={
                    "farmer_name": "Green Valley Farm",
                    "guide_url": "https://farmersmarketplace.com/farmer-guide",
                    "dashboard_url": "https://farmersmarketplace.com/dashboard"
                }
            )
            print(f"  ✅ Farmer welcome notification created: {farmer_welcome.id}")
            
            # Welcome buyer
            buyer_welcome = await notification_service.send_notification(
                db=db,
                user_id=buyer_id,
                notification_type=NotificationType.EMAIL,
                category=NotificationCategory.ACCOUNT,
                title="Welcome to Farmers Marketplace!",
                message="Welcome to fresh, local produce!",
                template_name="welcome_buyer",
                template_data={
                    "buyer_name": "John Smith",
                    "marketplace_url": "https://farmersmarketplace.com/marketplace"
                }
            )
            print(f"  ✅ Buyer welcome notification created: {buyer_welcome.id}")
            
        finally:
            await db.close()
        break


async def example_bulk_notifications():
    """Example: Send bulk notifications to multiple users."""
    print("\n📢 Example: Bulk Notifications")
    
    async for db in get_db():
        try:
            # Sample user IDs (replace with actual user IDs)
            user_ids = [uuid.uuid4() for _ in range(5)]
            
            # Send maintenance notice to all users
            notifications = await notification_service.send_bulk_notification(
                db=db,
                user_ids=user_ids,
                notification_type=NotificationType.EMAIL,
                category=NotificationCategory.SYSTEM,
                title="Scheduled Maintenance Notice",
                message="We will be performing maintenance on our system.",
                template_name="maintenance_notice",
                template_data={
                    "user_name": "Valued User",
                    "maintenance_date": "January 20, 2024",
                    "maintenance_time": "2:00 AM - 4:00 AM EST",
                    "estimated_duration": "2 hours",
                    "affected_services": "Web platform and mobile app"
                }
            )
            print(f"  ✅ Bulk maintenance notifications sent: {len(notifications)} users")
            
        finally:
            await db.close()
        break


async def example_notification_preferences():
    """Example: Manage user notification preferences."""
    print("\n⚙️ Example: Notification Preferences")
    
    async for db in get_db():
        try:
            user_id = uuid.uuid4()  # Replace with actual user ID
            
            # Update user preferences
            preferences = await notification_service.update_user_preferences(
                db=db,
                user_id=user_id,
                preferences={
                    "email_enabled": True,
                    "email_marketing": False,  # Disable marketing emails
                    "push_enabled": True,
                    "push_orders": True,
                    "push_products": False,    # Disable product push notifications
                    "quiet_hours_enabled": True,
                    "quiet_hours_start": "22:00",
                    "quiet_hours_end": "08:00"
                }
            )
            print(f"  ✅ User preferences updated: {preferences.id}")
            print(f"     - Email enabled: {preferences.email_enabled}")
            print(f"     - Marketing emails: {preferences.email_marketing}")
            print(f"     - Quiet hours: {preferences.quiet_hours_start} - {preferences.quiet_hours_end}")
            
        finally:
            await db.close()
        break


async def example_device_token_management():
    """Example: Manage device tokens for push notifications."""
    print("\n📱 Example: Device Token Management")
    
    async for db in get_db():
        try:
            user_id = uuid.uuid4()  # Replace with actual user ID
            
            # Register device tokens
            ios_token = await notification_service.register_device_token(
                db=db,
                user_id=user_id,
                token="ios_device_token_example_123456789",
                platform="ios"
            )
            print(f"  ✅ iOS device token registered: {ios_token.id}")
            
            android_token = await notification_service.register_device_token(
                db=db,
                user_id=user_id,
                token="android_device_token_example_987654321",
                platform="android"
            )
            print(f"  ✅ Android device token registered: {android_token.id}")
            
            web_token = await notification_service.register_device_token(
                db=db,
                user_id=user_id,
                token="web_push_token_example_abcdef123456",
                platform="web"
            )
            print(f"  ✅ Web push token registered: {web_token.id}")
            
        finally:
            await db.close()
        break


async def main():
    """Run all notification examples."""
    print("🌾 Farmers Marketplace - Notification System Examples")
    print("=" * 60)
    
    try:
        await example_new_order_notifications()
        await example_order_status_updates()
        await example_product_notifications()
        await example_welcome_notifications()
        await example_bulk_notifications()
        await example_notification_preferences()
        await example_device_token_management()
        
        print(f"\n🎉 All examples completed successfully!")
        print(f"   📧 Email notifications: Ready")
        print(f"   📱 Push notifications: Ready")
        print(f"   🔔 In-app notifications: Ready")
        print(f"   🎨 Template system: Ready")
        print(f"   ⚙️ User preferences: Ready")
        print(f"   🌐 Real-time WebSocket: Ready")
        
    except Exception as e:
        print(f"\n❌ Example failed: {str(e)}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
