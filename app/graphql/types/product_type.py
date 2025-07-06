import strawberry
from typing import Optional
from .farmer_type import FarmerType


@strawberry.type
class ProductCategoryType:
    id: int
    name: str
    description: Optional[str]


@strawberry.type
class ProductType:
    id: int
    name: str
    description: Optional[str]
    price: float
    stock: int
    seasonal_availability: Optional[str]
    category: Optional[ProductCategoryType]
    farmer: Optional[FarmerType]


@strawberry.input
class ProductSearchInput:
    name: Optional[str] = None
    category_id: Optional[int] = None
    farmer_id: Optional[int] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    available: Optional[bool] = None
    seasonal: Optional[str] = None
