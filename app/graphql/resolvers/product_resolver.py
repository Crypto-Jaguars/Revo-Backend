import strawberry
from typing import List, Optional, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models import ProductCategory, Farmer
from app.graphql.types.product_type import (
    ProductType,
    ProductCategoryType,
    ProductSearchInput,
)
from strawberry.types import Info
from app.services.search_service import search_products_service
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


@strawberry.type
class ProductResolver:
    @strawberry.field
    async def search_products(
        self, info: Info[Any, Any], filters: Optional[ProductSearchInput] = None
    ) -> List[ProductType]:
        session: AsyncSession = info.context["db"]
        return await search_products_service(session, filters)

    @strawberry.field
    async def products_by_category(
        self, info: Info[Any, Any]
    ) -> List[ProductCategoryType]:
        session: AsyncSession = info.context["db"]
        result = await session.execute(select(ProductCategory))
        categories = result.scalars().all() or []
        out = []
        for c in categories:
            out.append(
                ProductCategoryType(id=c.id, name=c.name, description=c.description)
            )
        return out

    @strawberry.field
    async def farmers_by_region(
        self, info: Info[Any, Any], region: str
    ) -> List[FarmerType]:
        session: AsyncSession = info.context["db"]
        result = await session.execute(
            select(Farmer).where(Farmer.location.ilike(f"%{region}%"))
        )
        farmers = result.scalars().all() or []
        out = []
        for f in farmers:
            out.append(
                FarmerType(
                    id=f.id,
                    name=f.name,
                    email=f.email,
                    phone=f.phone,
                    location=f.location,
                    verified=f.verified,
                )
            )
        return out
