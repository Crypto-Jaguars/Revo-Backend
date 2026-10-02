from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional

from app.database.session import SessionLocal
from app.models.products.inventory import (
    Inventory,
    ProductStockStatus,
    SeasonalAvailability,
    StockMovement,
)
from app.schemas.product import (
    InventoryCreate,
    InventoryResponse,
    InventoryUpdate,
    StockMovementCreate,
    StockMovementType,
)


class InventoryServiceError(Exception):
    pass


class InsufficientStockError(InventoryServiceError):
    pass


class InvalidSeasonError(InventoryServiceError):
    pass


class InventoryService:
    def __init__(self, db=SessionLocal):
        self.db = db

    def _get_inventory(self, inventory_id: int) -> Inventory:
        inventory = self.db.query(Inventory).filter(Inventory.id == inventory_id).first()
        if not inventory:
            raise InventoryServiceError(f"Inventory with id {inventory_id} not found")
        return inventory

    def _get_inventory_by_product(self, product_id: int) -> Optional[Inventory]:
        return (
            self.db.query(Inventory)
            .filter(Inventory.product_id == product_id)
            .first()
        )

    def create_inventory(
        self, product_id: int, data: InventoryCreate
    ) -> InventoryResponse:
        existing = self._get_inventory_by_product(product_id)
        if existing:
            raise InventoryServiceError(
                f"Inventory already exists for product {product_id}"
            )

        inventory = Inventory(
            product_id=product_id,
            stock_quantity=data.stock_quantity,
            reserved_quantity=data.reserved_quantity,
            reorder_level=data.reorder_level,
            supplier_lead_time_days=data.supplier_lead_time_days,
            season_start_date=data.season_start_date,
            season_end_date=data.season_end_date,
            current_stock_value=data.current_stock_value,
            status=data.status,
            notes=data.notes,
        )
        inventory.update_status()

        self.db.add(inventory)
        self.db.commit()
        self.db.refresh(inventory)

        return self._to_response(inventory)

    def get_inventory(self, inventory_id: int) -> InventoryResponse:
        inventory = self._get_inventory(inventory_id)
        return self._to_response(inventory)

    def get_inventory_by_product(self, product_id: int) -> Optional[InventoryResponse]:
        inventory = self._get_inventory_by_product(product_id)
        if not inventory:
            return None
        return self._to_response(inventory)

    def update_inventory(
        self, inventory_id: int, data: InventoryUpdate
    ) -> InventoryResponse:
        inventory = self._get_inventory(inventory_id)

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(inventory, field, value)

        inventory.update_status()
        self.db.commit()
        self.db.refresh(inventory)

        return self._to_response(inventory)

    def get_available_quantity(self, inventory_id: int) -> int:
        inventory = self._get_inventory(inventory_id)
        return inventory.available_quantity

    def add_stock(
        self, inventory_id: int, quantity: int, note: Optional[str] = None
    ) -> InventoryResponse:
        if quantity <= 0:
            raise InventoryServiceError("Quantity must be positive")

        inventory = self._get_inventory(inventory_id)
        inventory.add_stock(quantity, note)

        movement = StockMovement(
            inventory_id=inventory_id,
            movement_type="incoming",
            quantity=quantity,
            notes=note,
        )
        self.db.add(movement)
        self.db.commit()
        self.db.refresh(inventory)

        return self._to_response(inventory)

    def remove_stock(
        self, inventory_id: int, quantity: int, note: Optional[str] = None
    ) -> InventoryResponse:
        if quantity <= 0:
            raise InventoryServiceError("Quantity must be positive")

        inventory = self._get_inventory(inventory_id)
        inventory.remove_stock(quantity, note)

        movement = StockMovement(
            inventory_id=inventory_id,
            movement_type="outgoing",
            quantity=quantity,
            notes=note,
        )
        self.db.add(movement)
        self.db.commit()
        self.db.refresh(inventory)

        return self._to_response(inventory)

    def reserve_stock(self, inventory_id: int, quantity: int) -> InventoryResponse:
        if quantity <= 0:
            raise InventoryServiceError("Quantity must be positive")

        inventory = self._get_inventory(inventory_id)
        inventory.reserve_stock(quantity)
        inventory.update_status()
        self.db.commit()
        self.db.refresh(inventory)

        return self._to_response(inventory)

    def release_reservation(self, inventory_id: int, quantity: int) -> InventoryResponse:
        if quantity <= 0:
            raise InventoryServiceError("Quantity must be positive")

        inventory = self._get_inventory(inventory_id)
        inventory.release_reservation(quantity)
        inventory.update_status()
        self.db.commit()
        self.db.refresh(inventory)

        return self._to_response(inventory)

    def get_seasonal_status(
        self, inventory_id: int, check_date: Optional[date] = None
    ) -> SeasonalAvailability:
        inventory = self._get_inventory(inventory_id)
        return inventory._get_seasonal_status(check_date)

    def update_all_availability_statuses(self) -> int:
        inventories = self.db.query(Inventory).all()
        updated_count = 0
        for inventory in inventories:
            old_status = inventory.status
            inventory.update_status()
            if inventory.status != old_status:
                updated_count += 1
        self.db.commit()
        return updated_count

    def get_stock_movements(
        self, inventory_id: int, limit: int = 50
    ) -> List[StockMovement]:
        inventory = self._get_inventory(inventory_id)
        return (
            self.db.query(StockMovement)
            .filter(StockMovement.inventory_id == inventory_id)
            .order_by(StockMovement.created_at.desc())
            .limit(limit)
            .all()
        )

    def _to_response(self, inventory: Inventory) -> InventoryResponse:
        return InventoryResponse(
            id=inventory.id,
            product_id=inventory.product_id,
            stock_quantity=inventory.stock_quantity,
            reserved_quantity=inventory.reserved_quantity,
            reorder_level=inventory.reorder_level,
            supplier_lead_time_days=inventory.supplier_lead_time_days,
            season_start_date=inventory.season_start_date.date()
            if inventory.season_start_date
            else None,
            season_end_date=inventory.season_end_date.date()
            if inventory.season_end_date
            else None,
            current_stock_value=inventory.current_stock_value,
            status=inventory.status,
            notes=inventory.notes,
            available_quantity=inventory.available_quantity,
            is_in_stock=inventory.is_in_stock,
            is_below_reorder_level=inventory.is_below_reorder_level,
        )


inventory_service = InventoryService()
