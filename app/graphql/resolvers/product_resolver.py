import strawberry
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models import ProductCategory
from app.graphql.types.product_type import (
    ProductType,
    ProductCategoryType,
    ProductSearchInput,
)
from app.services.search_service import search_products_service


@strawberry.type
class ProductResolver:
    @strawberry.field
    async def search_products(
        self, info: strawberry.Info, filters: ProductSearchInput | None = None
    ) -> List[ProductType]:
        session: AsyncSession = info.context["db"]
        return await search_products_service(session, filters)

    @strawberry.field
    async def product_categories(
        self, info: strawberry.Info, limit: int = 100, offset: int = 0
    ) -> List[ProductCategoryType]:
        session: AsyncSession = info.context["db"]
        result = await session.execute(
            select(ProductCategory).limit(limit).offset(offset)
        )
        categories = result.scalars().all() or []
        return [
            ProductCategoryType(id=c.id, name=c.name, description=c.description)
            for c in categories
        ]
