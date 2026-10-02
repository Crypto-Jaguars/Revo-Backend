from __future__ import annotations

from datetime import date
from decimal import Decimal
from enum import Enum
from typing import Optional

from app.database.session import get_db
from app.models.base import Base, TimestampMixin
from sqlalchemy import Column, DateTime, Enum as SQLAlchemyEnum, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import relationship


class ProductStockStatus(str, Enum):
    AVAILABLE = "available"
    OUT_OF_STOCK = "out_of_stock"
    COMING_SOON = "coming_soon"
    OUT_OF_SEASON = "out_of_season"


class SeasonalAvailability(str, Enum):
    IN_SEASON = "in_season"
    OUT_OF_SEASON = "out_of_season"
    COMING_SOON = "coming_soon"


class Inventory(Base, TimestampMixin):
    __tablename__ = "inventory"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(
        Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    stock_quantity = Column(Integer, nullable=False, default=0)
    reserved_quantity = Column(Integer, nullable=False, default=0)
    reorder_level = Column(Integer, nullable=False, default=10)
    supplier_lead_time_days = Column(Integer, nullable=False, default=7)

    season_start_date = Column(DateTime, nullable=True)
    season_end_date = Column(DateTime, nullable=True)
    current_stock_value = Column(Numeric(15, 2), nullable=False, default=0.00)

    status = Column(
        SQLAlchemyEnum(ProductStockStatus),
        nullable=False,
        default=ProductStockStatus.AVAILABLE,
    )

    last_stock_count_date = Column(DateTime, nullable=True)
    notes = Column(String(500), nullable=True)

    product = relationship("Product", back_populates="inventory")

    @property
    def available_quantity(self) -> int:
        return max(0, self.stock_quantity - self.reserved_quantity)

    @property
    def is_in_stock(self) -> bool:
        return self.available_quantity > 0

    @property
    def is_below_reorder_level(self) -> bool:
        return self.available_quantity < self.reorder_level

    def _get_seasonal_status(self, check_date: Optional[date] = None) -> SeasonalAvailability:
        check = check_date or date.today()

        if self.season_start_date is None and self.season_end_date is None:
            return SeasonalAvailability.IN_SEASON

        if self.season_start_date is not None:
            season_start = self.season_start_date.date() if hasattr(self.season_start_date, "date") else self.season_start_date
            if check < season_start:
                return SeasonalAvailability.COMING_SOON

        if self.season_end_date is not None:
            season_end = self.season_end_date.date() if hasattr(self.season_end_date, "date") else self.season_end_date
            if check > season_end:
                return SeasonalAvailability.OUT_OF_SEASON

        return SeasonalAvailability.IN_SEASON

    def calculate_availability_status(self, check_date: Optional[date] = None) -> ProductStockStatus:
        seasonal = self._get_seasonal_status(check_date)

        if seasonal == SeasonalAvailability.COMING_SOON:
            return ProductStockStatus.COMING_SOON

        if seasonal == SeasonalAvailability.OUT_OF_SEASON:
            return ProductStockStatus.OUT_OF_SEASON

        if self.available_quantity == 0:
            return ProductStockStatus.OUT_OF_STOCK

        if self.is_below_reorder_level:
            return ProductStockStatus.AVAILABLE

        return ProductStockStatus.AVAILABLE

    def update_status(self, check_date: Optional[date] = None) -> ProductStockStatus:
        new_status = self.calculate_availability_status(check_date)
        self.status = new_status
        return new_status

    def add_stock(self, quantity: int, note: Optional[str] = None) -> None:
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        self.stock_quantity += quantity
        self._recalculate_values(note)

    def remove_stock(self, quantity: int, note: Optional[str] = None) -> None:
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        if quantity > self.available_quantity:
            raise ValueError("Insufficient stock available")
        self.stock_quantity -= quantity
        self._recalculate_values(note)

    def reserve_stock(self, quantity: int) -> None:
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        if quantity > self.available_quantity:
            raise ValueError("Insufficient available stock to reserve")
        self.reserved_quantity += quantity

    def release_reservation(self, quantity: int) -> None:
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        if quantity > self.reserved_quantity:
            raise ValueError("Reservation quantity exceeds current reservation")
        self.reserved_quantity -= quantity

    def _recalculate_values(self, note: Optional[str] = None) -> None:
        self.update_status()
        if note:
            existing = self.notes or ""
            self.notes = f"{existing}; {note}" if existing else note

    def __repr__(self) -> str:
        return (
            f"<Inventory(id={self.id}, product_id={self.product_id}, "
            f"stock={self.stock_quantity}, status={self.status.value})>"
        )


class StockMovement(Base, TimestampMixin):
    __tablename__ = "stock_movements"

    id = Column(Integer, primary_key=True, index=True)
    inventory_id = Column(
        Integer, ForeignKey("inventory.id", ondelete="CASCADE"), nullable=False
    )
    movement_type = Column(
        SQLAlchemyEnum("incoming", "outgoing", "adjustment", "return"),
        nullable=False,
    )
    quantity = Column(Integer, nullable=False)
    reference_type = Column(String(50), nullable=True)
    reference_id = Column(Integer, nullable=True)
    notes = Column(String(500), nullable=True)

    inventory = relationship("Inventory", back_populates="movements")

    @property
    def net_quantity(self) -> int:
        if self.movement_type in ("incoming", "return"):
            return self.quantity
        return -self.quantity

    def __repr__(self) -> str:
        return (
            f"<StockMovement(id={self.id}, type={self.movement_type}, "
            f"quantity={self.quantity}, inventory_id={self.inventory_id})>"
        )


Inventory.movements = relationship(
    "StockMovement",
    back_populates="inventory",
    order_by="StockMovement.created_at.desc()",
    cascade="all, delete-orphan",
)
