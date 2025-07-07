from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.sql import Select
from app.models import Product
from app.graphql.types.product_type import (
    ProductType,
    ProductSearchInput,
)
from app.services.helpers import get_product_category, get_farmer


def _apply_filters(query: Select, filters: ProductSearchInput) -> Select:
    if filters.name:
        query = query.where(Product.name.ilike(f"%{filters.name}%"))
    if filters.category_id:
        query = query.where(Product.category_id == filters.category_id)
    if filters.farmer_id:
        query = query.where(Product.farmer_id == filters.farmer_id)
    if filters.min_price:
        query = query.where(Product.price >= filters.min_price)
    if filters.max_price:
        query = query.where(Product.price <= filters.max_price)
    if filters.available is not None:
        if filters.available:
            query = query.where(Product.stock > 0)
        else:
            query = query.where(Product.stock == 0)
    if filters.seasonal:
        query = query.where(
            Product.seasonal_availability.ilike(f"%{filters.seasonal}%")
        )
    return query


async def search_products_service(
    session: AsyncSession, filters: Optional[ProductSearchInput] = None
) -> List[ProductType]:
    query = select(Product)
    if filters:
        query = _apply_filters(query, filters)

    result = await session.execute(query)
    products = result.scalars().all()
    out = []
    for p in products:
        category = await get_product_category(session, p.category_id)
        farmer = await get_farmer(session, p.farmer_id)
        # Handle missing entities gracefully as expected by tests
        out.append(
            ProductType(
                id=p.id,
                name=p.name,
                description=p.description,
                price=p.price,
                stock=p.stock,
                seasonal_availability=p.seasonal_availability,
                category=category,
                farmer=farmer,
            )
        )
    return out
