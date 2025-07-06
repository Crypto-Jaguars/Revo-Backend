import strawberry
from typing import List, Optional, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models import ProductCategory
from app.graphql.types.product_type import (
    ProductType,
    ProductCategoryType,
    ProductSearchInput,
)
from strawberry.types import Info
from app.services.search_service import search_products_service


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
