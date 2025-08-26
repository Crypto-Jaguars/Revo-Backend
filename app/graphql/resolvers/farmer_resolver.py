from __future__ import annotations
from typing import Optional, List
from uuid import UUID

import strawberry
from fastapi import HTTPException
from sqlalchemy import select
from strawberry.exceptions import StrawberryGraphQLError

from app.core.database import get_db
from app.graphql.types.farmer_type import Farmer, FarmerInput, FarmerUpdateInput
from app.graphql.types.farmer_type import Location as GqlLocation
from app.models.farmers.farmer import Farmer as FarmerModel
from app.services.farmer_service import FarmerService
from app.services.auth_service import auth_service

@strawberry.type
class FarmerQuery:
    """Farmer-related GraphQL queries."""

    @strawberry.field
    async def farmer(self, id: UUID) -> Optional[Farmer]:
        async for db in get_db():
            result = await db.execute(select(FarmerModel).where(FarmerModel.id == id))
            model = result.scalar_one_or_none()
            return Farmer.from_model(model) if model else None
        return None

    @strawberry.field
    async def farmers(self, skip: int = 0, limit: int = 100) -> List[Farmer]:
        async for db in get_db():
            result = await db.execute(select(FarmerModel).offset(skip).limit(limit))
            models = result.scalars().all()
            return [Farmer.from_model(m) for m in models]
        return []

    @strawberry.field
    async def farmers_by_location(
        self,
        latitude: float,
        longitude: float,
        radius_km: float = 10.0,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Farmer]:
        """
        Search farmers by location using the service's geo search.
        """
        async for db in get_db():
            try:
                farmers = await FarmerService.search_farmers_by_location(
                    db=db,
                    latitude=latitude,
                    longitude=longitude,
                    radius_km=radius_km,
                    skip=skip,
                    limit=limit,
                )
                return [Farmer.from_model(f) for f in farmers]
            except Exception:
                raise StrawberryGraphQLError("Failed to search farmers by location")
        return []

@strawberry.type
class FarmerMutation:
    """Farmer-related GraphQL mutations (auth required)."""

    @strawberry.field
    async def create_farmer(self, farmer_input: FarmerInput, token: str) -> Farmer:
        from app.schemas.farmer import FarmerCreate
        from app.schemas.location import LocationCreate

        async for db in get_db():
            try:
                # auth check
                await auth_service.get_current_user_from_token(db, token)

                # map inputs
                location_schema = None
                if farmer_input.location:
                    li = farmer_input.location
                    location_schema = LocationCreate(
                        latitude=li.latitude,
                        longitude=li.longitude,
                        address=li.address,
                        city=li.city,
                        state=li.state,
                        country=li.country,
                    )

                create_schema = FarmerCreate(
                    user_id=farmer_input.user_id,
                    farm_name=farmer_input.farm_name,
                    farm_size=farmer_input.farm_size,
                    organic_certified=farmer_input.organic_certified,
                    description=farmer_input.description,
                    location=location_schema,
                )

                model = await FarmerService.create_farmer(db, create_schema)
                return Farmer.from_model(model)
            except HTTPException:
                # invalid token / unauthenticated
                raise StrawberryGraphQLError("Authentication required")
            except Exception:
                raise StrawberryGraphQLError("Failed to create farmer")
        raise RuntimeError("Database session not available")

    @strawberry.field
    async def update_farmer(self, id: UUID, farmer_input: FarmerUpdateInput, token: str) -> Optional[Farmer]:
        from app.schemas.farmer import FarmerUpdate
        from app.schemas.location import LocationCreate

        async for db in get_db():
            try:
                # auth check
                await auth_service.get_current_user_from_token(db, token)

                location_schema = None
                if farmer_input.location:
                    li = farmer_input.location
                    location_schema = LocationCreate(
                        latitude=li.latitude,
                        longitude=li.longitude,
                        address=li.address,
                        city=li.city,
                        state=li.state,
                        country=li.country,
                    )

                update_schema = FarmerUpdate(
                    farm_name=farmer_input.farm_name,
                    farm_size=farmer_input.farm_size,
                    organic_certified=farmer_input.organic_certified,
                    description=farmer_input.description,
                    location=location_schema,
                )

                model = await FarmerService.update_farmer(db, id, update_schema)
                return Farmer.from_model(model) if model else None
            except HTTPException:
                raise StrawberryGraphQLError("Authentication required")
            except Exception:
                raise StrawberryGraphQLError("Failed to update farmer")
        return None
