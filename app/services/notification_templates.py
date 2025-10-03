"""
Predefined notification templates for the Farmers Marketplace.

Templates for: new orders, status updates, reminders, and system notifications.
"""

from typing import Dict, List

from app.models.shared.notification import NotificationCategory, NotificationType


class NotificationTemplates:
    """Predefined notification templates."""
    
    @staticmethod
    def get_default_templates() -> List[Dict]:
        """Get all default notification templates."""
        return [
            # Order Templates
            {
                "name": "new_order_farmer",
                "category": NotificationCategory.ORDER,
                "notification_type": NotificationType.EMAIL,
                "subject_template": "🛒 New Order Received - Order #{{ order_id }}",
                "body_template": """
                <h2>New Order Received!</h2>
                <p>Hello {{ farmer_name }},</p>
                <p>You have received a new order from {{ buyer_name }}.</p>
                
                <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h3>Order Details:</h3>
                    <ul>
                        <li><strong>Order ID:</strong> #{{ order_id }}</li>
                        <li><strong>Customer:</strong> {{ buyer_name }}</li>
                        <li><strong>Total Amount:</strong> ${{ total_amount }}</li>
                        <li><strong>Items:</strong> {{ item_count }} items</li>
                        <li><strong>Delivery Date:</strong> {{ delivery_date }}</li>
                    </ul>
                </div>
                
                <p>Please log in to your dashboard to review and confirm this order.</p>
                <p><a href="{{ dashboard_url }}" style="background-color: #28a745; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">View Order</a></p>
                
                <p>Best regards,<br>Farmers Marketplace Team</p>
                """,
                "variables": {
                    "farmer_name": "string",
                    "buyer_name": "string", 
                    "order_id": "string",
                    "total_amount": "number",
                    "item_count": "number",
                    "delivery_date": "string",
                    "dashboard_url": "string"
                }
            },
            
            {
                "name": "new_order_buyer",
                "category": NotificationCategory.ORDER,
                "notification_type": NotificationType.EMAIL,
                "subject_template": "✅ Order Confirmed - Order #{{ order_id }}",
                "body_template": """
                <h2>Order Confirmation</h2>
                <p>Hello {{ buyer_name }},</p>
                <p>Thank you for your order! We've received your order and it's being processed.</p>
                
                <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h3>Order Summary:</h3>
                    <ul>
                        <li><strong>Order ID:</strong> #{{ order_id }}</li>
                        <li><strong>Farmer:</strong> {{ farmer_name }}</li>
                        <li><strong>Total Amount:</strong> ${{ total_amount }}</li>
                        <li><strong>Expected Delivery:</strong> {{ delivery_date }}</li>
                    </ul>
                </div>
                
                <p>You will receive updates as your order is processed and prepared for delivery.</p>
                <p><a href="{{ order_url }}" style="background-color: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Track Order</a></p>
                
                <p>Best regards,<br>Farmers Marketplace Team</p>
                """,
                "variables": {
                    "buyer_name": "string",
                    "farmer_name": "string",
                    "order_id": "string", 
                    "total_amount": "number",
                    "delivery_date": "string",
                    "order_url": "string"
                }
            },
            
            # Order Status Updates
            {
                "name": "order_status_update",
                "category": NotificationCategory.ORDER,
                "notification_type": NotificationType.PUSH,
                "subject_template": "Order #{{ order_id }} - {{ status_name }}",
                "body_template": "Your order from {{ farmer_name }} is now {{ status_name }}. {{ status_message }}",
                "variables": {
                    "order_id": "string",
                    "farmer_name": "string",
                    "status_name": "string",
                    "status_message": "string"
                }
            },
            
            {
                "name": "order_ready_pickup",
                "category": NotificationCategory.ORDER,
                "notification_type": NotificationType.EMAIL,
                "subject_template": "📦 Order Ready for Pickup - Order #{{ order_id }}",
                "body_template": """
                <h2>Your Order is Ready!</h2>
                <p>Hello {{ buyer_name }},</p>
                <p>Great news! Your order from {{ farmer_name }} is ready for pickup.</p>
                
                <div style="background-color: #e8f5e8; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h3>Pickup Details:</h3>
                    <ul>
                        <li><strong>Order ID:</strong> #{{ order_id }}</li>
                        <li><strong>Pickup Location:</strong> {{ pickup_address }}</li>
                        <li><strong>Available Hours:</strong> {{ pickup_hours }}</li>
                        <li><strong>Contact:</strong> {{ farmer_phone }}</li>
                    </ul>
                </div>
                
                <p>Please bring your order confirmation when picking up.</p>
                <p><a href="{{ directions_url }}" style="background-color: #28a745; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Get Directions</a></p>
                
                <p>Best regards,<br>Farmers Marketplace Team</p>
                """,
                "variables": {
                    "buyer_name": "string",
                    "farmer_name": "string",
                    "order_id": "string",
                    "pickup_address": "string",
                    "pickup_hours": "string",
                    "farmer_phone": "string",
                    "directions_url": "string"
                }
            },
            
            # Product Templates
            {
                "name": "product_low_stock",
                "category": NotificationCategory.PRODUCT,
                "notification_type": NotificationType.IN_APP,
                "subject_template": "Low Stock Alert",
                "body_template": "Your product '{{ product_name }}' is running low ({{ current_stock }} remaining). Consider restocking soon.",
                "variables": {
                    "product_name": "string",
                    "current_stock": "number"
                }
            },
            
            {
                "name": "product_out_of_stock",
                "category": NotificationCategory.PRODUCT,
                "notification_type": NotificationType.EMAIL,
                "subject_template": "⚠️ Product Out of Stock - {{ product_name }}",
                "body_template": """
                <h2>Product Out of Stock</h2>
                <p>Hello {{ farmer_name }},</p>
                <p>Your product <strong>{{ product_name }}</strong> is now out of stock and has been automatically hidden from the marketplace.</p>
                
                <div style="background-color: #fff3cd; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h3>Action Required:</h3>
                    <p>To make this product available again, please:</p>
                    <ol>
                        <li>Update your inventory levels</li>
                        <li>Reactivate the product listing</li>
                    </ol>
                </div>
                
                <p><a href="{{ product_url }}" style="background-color: #ffc107; color: black; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Update Product</a></p>
                
                <p>Best regards,<br>Farmers Marketplace Team</p>
                """,
                "variables": {
                    "farmer_name": "string",
                    "product_name": "string",
                    "product_url": "string"
                }
            },
            
            {
                "name": "new_product_approved",
                "category": NotificationCategory.PRODUCT,
                "notification_type": NotificationType.EMAIL,
                "subject_template": "✅ Product Approved - {{ product_name }}",
                "body_template": """
                <h2>Product Approved!</h2>
                <p>Hello {{ farmer_name }},</p>
                <p>Congratulations! Your product <strong>{{ product_name }}</strong> has been approved and is now live on the marketplace.</p>
                
                <div style="background-color: #e8f5e8; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h3>What's Next:</h3>
                    <ul>
                        <li>Your product is now visible to customers</li>
                        <li>You'll receive notifications for new orders</li>
                        <li>Monitor your sales in the dashboard</li>
                    </ul>
                </div>
                
                <p><a href="{{ product_url }}" style="background-color: #28a745; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">View Product</a></p>
                
                <p>Best regards,<br>Farmers Marketplace Team</p>
                """,
                "variables": {
                    "farmer_name": "string",
                    "product_name": "string",
                    "product_url": "string"
                }
            },
            
            # Account Templates
            {
                "name": "welcome_farmer",
                "category": NotificationCategory.ACCOUNT,
                "notification_type": NotificationType.EMAIL,
                "subject_template": "🌾 Welcome to Farmers Marketplace!",
                "body_template": """
                <h2>Welcome to Farmers Marketplace!</h2>
                <p>Hello {{ farmer_name }},</p>
                <p>Welcome to our community of farmers and agricultural producers! We're excited to have you join us.</p>
                
                <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h3>Getting Started:</h3>
                    <ol>
                        <li><strong>Complete your profile:</strong> Add your farm details and photos</li>
                        <li><strong>Add your products:</strong> List your fresh produce and goods</li>
                        <li><strong>Set your availability:</strong> Configure pickup times and locations</li>
                        <li><strong>Start selling:</strong> Connect with local customers</li>
                    </ol>
                </div>
                
                <p>Need help? Check out our <a href="{{ guide_url }}">Farmer's Guide</a> or contact our support team.</p>
                <p><a href="{{ dashboard_url }}" style="background-color: #28a745; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Go to Dashboard</a></p>
                
                <p>Happy farming!<br>Farmers Marketplace Team</p>
                """,
                "variables": {
                    "farmer_name": "string",
                    "guide_url": "string",
                    "dashboard_url": "string"
                }
            },
            
            {
                "name": "welcome_buyer",
                "category": NotificationCategory.ACCOUNT,
                "notification_type": NotificationType.EMAIL,
                "subject_template": "🛒 Welcome to Farmers Marketplace!",
                "body_template": """
                <h2>Welcome to Farmers Marketplace!</h2>
                <p>Hello {{ buyer_name }},</p>
                <p>Welcome to the freshest marketplace in town! We're thrilled to help you connect with local farmers and get the best fresh produce.</p>
                
                <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h3>Start Shopping:</h3>
                    <ul>
                        <li><strong>Browse local farms:</strong> Discover farmers in your area</li>
                        <li><strong>Fresh products:</strong> Find seasonal fruits, vegetables, and more</li>
                        <li><strong>Direct from farm:</strong> Support local agriculture</li>
                        <li><strong>Easy pickup:</strong> Convenient pickup locations and times</li>
                    </ul>
                </div>
                
                <p><a href="{{ marketplace_url }}" style="background-color: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Start Shopping</a></p>
                
                <p>Happy shopping!<br>Farmers Marketplace Team</p>
                """,
                "variables": {
                    "buyer_name": "string",
                    "marketplace_url": "string"
                }
            },
            
            {
                "name": "password_reset",
                "category": NotificationCategory.ACCOUNT,
                "notification_type": NotificationType.EMAIL,
                "subject_template": "🔒 Password Reset Request",
                "body_template": """
                <h2>Password Reset Request</h2>
                <p>Hello {{ user_name }},</p>
                <p>We received a request to reset your password for your Farmers Marketplace account.</p>
                
                <div style="background-color: #fff3cd; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <p><strong>If you requested this:</strong> Click the button below to reset your password.</p>
                    <p><strong>If you didn't request this:</strong> You can safely ignore this email.</p>
                </div>
                
                <p><a href="{{ reset_url }}" style="background-color: #dc3545; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Reset Password</a></p>
                
                <p><small>This link will expire in {{ expiry_hours }} hours for security.</small></p>
                
                <p>Best regards,<br>Farmers Marketplace Team</p>
                """,
                "variables": {
                    "user_name": "string",
                    "reset_url": "string",
                    "expiry_hours": "number"
                }
            },
            
            # Reminder Templates
            {
                "name": "order_reminder_farmer",
                "category": NotificationCategory.ORDER,
                "notification_type": NotificationType.PUSH,
                "subject_template": "Order Reminder",
                "body_template": "Don't forget to prepare order #{{ order_id }} for {{ buyer_name }}. Pickup scheduled for {{ pickup_date }}.",
                "variables": {
                    "order_id": "string",
                    "buyer_name": "string",
                    "pickup_date": "string"
                }
            },
            
            {
                "name": "profile_incomplete_reminder",
                "category": NotificationCategory.ACCOUNT,
                "notification_type": NotificationType.IN_APP,
                "subject_template": "Complete Your Profile",
                "body_template": "Your profile is {{ completion_percentage }}% complete. Add more details to attract more customers!",
                "variables": {
                    "completion_percentage": "number"
                }
            },
            
            # System Templates
            {
                "name": "maintenance_notice",
                "category": NotificationCategory.SYSTEM,
                "notification_type": NotificationType.EMAIL,
                "subject_template": "🔧 Scheduled Maintenance Notice",
                "body_template": """
                <h2>Scheduled Maintenance</h2>
                <p>Hello {{ user_name }},</p>
                <p>We will be performing scheduled maintenance on Farmers Marketplace to improve your experience.</p>
                
                <div style="background-color: #e7f3ff; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h3>Maintenance Details:</h3>
                    <ul>
                        <li><strong>Date:</strong> {{ maintenance_date }}</li>
                        <li><strong>Time:</strong> {{ maintenance_time }}</li>
                        <li><strong>Duration:</strong> {{ estimated_duration }}</li>
                        <li><strong>Services Affected:</strong> {{ affected_services }}</li>
                    </ul>
                </div>
                
                <p>We apologize for any inconvenience and appreciate your patience.</p>
                
                <p>Best regards,<br>Farmers Marketplace Team</p>
                """,
                "variables": {
                    "user_name": "string",
                    "maintenance_date": "string",
                    "maintenance_time": "string",
                    "estimated_duration": "string",
                    "affected_services": "string"
                }
            },
            
            {
                "name": "new_feature_announcement",
                "category": NotificationCategory.SYSTEM,
                "notification_type": NotificationType.IN_APP,
                "subject_template": "🎉 New Feature: {{ feature_name }}",
                "body_template": "Check out our new feature: {{ feature_name }}! {{ feature_description }}",
                "variables": {
                    "feature_name": "string",
                    "feature_description": "string"
                }
            }
        ]


# Template helper functions
def get_order_templates() -> List[Dict]:
    """Get order-related templates."""
    templates = NotificationTemplates.get_default_templates()
    return [t for t in templates if t["category"] == NotificationCategory.ORDER]


def get_product_templates() -> List[Dict]:
    """Get product-related templates."""
    templates = NotificationTemplates.get_default_templates()
    return [t for t in templates if t["category"] == NotificationCategory.PRODUCT]


def get_account_templates() -> List[Dict]:
    """Get account-related templates."""
    templates = NotificationTemplates.get_default_templates()
    return [t for t in templates if t["category"] == NotificationCategory.ACCOUNT]


def get_system_templates() -> List[Dict]:
    """Get system-related templates."""
    templates = NotificationTemplates.get_default_templates()
    return [t for t in templates if t["category"] == NotificationCategory.SYSTEM]
