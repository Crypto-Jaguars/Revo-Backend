"""
Product-related models for the agricultural marketplace.

TODO: Contributors should implement:
- Product base model with agricultural details
- ProductCategory for organizing products
- SeasonalAvailability for harvest scheduling
- ProductImage for product photos
- ProductVariant for different sizes/qualities

"""

# TODO: Implement product models
from .product import Product
from .category import ProductCategory

__all__ = [
    "Product",
    "ProductCategory",
]
