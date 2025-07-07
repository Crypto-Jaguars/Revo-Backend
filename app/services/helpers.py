from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import ProductCategory, Farmer
from app.graphql.types.product_type import ProductCategoryType
from app.graphql.types.farmer_type import FarmerType


async def get_product_category(
    session: AsyncSession, category_id: int
) -> Optional[ProductCategoryType]:
    category = await session.get(ProductCategory, category_id)
    if not category:
        return None
    return ProductCategoryType(
        id=category.id, name=category.name, description=category.description
    )


async def get_farmer(session: AsyncSession, farmer_id: int) -> Optional[FarmerType]:
    farmer = await session.get(Farmer, farmer_id)
    if not farmer:
        return None
    return FarmerType(
        id=farmer.id,
        name=farmer.name,
        email=farmer.email,
        phone=farmer.phone,
        location=farmer.location,
        verified=farmer.verified,
    )
