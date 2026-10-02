from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class ProductStockStatus(str, Enum):
    AVAILABLE = "available"
    OUT_OF_STOCK = "out_of_stock"
    COMING_SOON = "coming_soon"
    OUT_OF_SEASON = "out_of_season"


class SeasonalAvailability(str, Enum):
    IN_SEASON = "in_season"
    OUT_OF_SEASON = "out_of_season"
    COMING_SOON = "coming_soon"


class InventoryBase(BaseModel):
    stock_quantity: int = Field(..., ge=0)
    reserved_quantity: int = Field(default=0, ge=0)
    reorder_level: int = Field(default=10, ge=0)
    supplier_lead_time_days: int = Field(default=7, ge=0)

    season_start_date: Optional[date] = None
    season_end_date: Optional[date] = None
    current_stock_value: Decimal = Field(default=Decimal("0.00"), ge=0)

    status: ProductStockStatus = ProductStockStatus.AVAILABLE

    notes: Optional[str] = Field(default=None, max_length=500)

    class Config:
        from_attributes = True


class InventoryCreate(InventoryBase):
    pass


class InventoryUpdate(BaseModel):
    stock_quantity: Optional[int] = Field(default=None, ge=0)
    reserved_quantity: Optional[int] = Field(default=None, ge=0)
    reorder_level: Optional[int] = Field(default=None, ge=0)
    supplier_lead_time_days: Optional[int] = Field(default=None, ge=0)

    season_start_date: Optional[date] = None
    season_end_date: Optional[date] = None
    current_stock_value: Optional[Decimal] = Field(default=None, ge=0)

    notes: Optional[str] = Field(default=None, max_length=500)


class InventoryResponse(InventoryBase):
    id: int
    product_id: int
    available_quantity: int = 0
    is_in_stock: bool = False
    is_below_reorder_level: bool = False

    class Config:
        from_attributes = True


class StockMovementType(str, Enum):
    INCOMING = "incoming"
    OUTGOING = "outgoing"
    ADJUSTMENT = "adjustment"
    RETURN = "return"


class StockMovementCreate(BaseModel):
    movement_type: StockMovementType
    quantity: int = Field(..., ge=1)
    reference_type: Optional[str] = Field(default=None, max_length=50)
    reference_id: Optional[int] = None
    notes: Optional[str] = Field(default=None, max_length=500)


class StockMovementResponse(BaseModel):
    id: int
    inventory_id: int
    movement_type: str
    quantity: int
    reference_type: Optional[str] = None
    reference_id: Optional[int] = None
    notes: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ProductDetail(BaseModel):
    id: int
    name: str
    sku: str
    description: Optional[str] = None
    base_price: Decimal
    category: Optional[str] = None
    status: ProductStockStatus
    inventory: Optional[InventoryResponse] = None
    movements: List[StockMovementResponse] = Field(default_factory=list)
    created_at: datetime

    class Config:
        from_attributes = True


class ProductFilter(BaseModel):
    status: Optional[ProductStockStatus] = None
    category: Optional[str] = None
    in_stock: Optional[bool] = None
    in_season: Optional[bool] = None
    min_price: Optional[Decimal] = None
    max_price: Optional[Decimal] = None
    search: Optional[str] = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
