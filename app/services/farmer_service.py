from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.models import Farmer, User
from app.schemas.farmer import FarmerCreate, FarmerUpdate


class FarmerService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_farmer_profile(self, user_id: int, farmer_data: FarmerCreate) -> Farmer:
        """Create a new farmer profile for a user."""
        # Check if user exists
        user_result = await self.db.execute(select(User).where(User.id == user_id))
        user = user_result.scalar_one_or_none()
        
        if not user:
            raise ValueError("User not found")
        
        # Check if farmer profile already exists
        existing_farmer = await self.get_farmer_by_user_id(user_id)
        if existing_farmer:
            raise ValueError("Farmer profile already exists for this user")
        
        # Create farmer profile with transaction handling
        try:
            farmer = Farmer(
                user_id=user_id,
                **farmer_data.model_dump()
            )
            
            self.db.add(farmer)
            await self.db.commit()
            await self.db.refresh(farmer)
            
            return farmer
        except Exception:
            await self.db.rollback()
            raise

    async def get_farmer_by_id(self, farmer_id: int) -> Optional[Farmer]:
        """Get farmer by ID."""
        result = await self.db.execute(
            select(Farmer)
            .options(selectinload(Farmer.user))
            .where(Farmer.id == farmer_id)
        )
        return result.scalar_one_or_none()

    async def get_farmer_by_user_id(self, user_id: int) -> Optional[Farmer]:
        """Get farmer by user ID."""
        result = await self.db.execute(
            select(Farmer)
            .options(selectinload(Farmer.user))
            .where(Farmer.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def update_farmer_profile(self, farmer_id: int, farmer_data: FarmerUpdate) -> Optional[Farmer]:
        """Update farmer profile."""
        farmer = await self.get_farmer_by_id(farmer_id)
        
        if not farmer:
            return None
        
        # Update only provided fields
        update_data = farmer_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(farmer, field, value)
        
        try:
            await self.db.commit()
            await self.db.refresh(farmer)
            return farmer
        except Exception:
            await self.db.rollback()
            raise

    async def delete_farmer_profile(self, farmer_id: int) -> bool:
        """Delete farmer profile."""
        farmer = await self.get_farmer_by_id(farmer_id)
        
        if not farmer:
            return False
        
        try:
            await self.db.delete(farmer)
            await self.db.commit()
            return True
        except Exception:
            await self.db.rollback()
            raise

    async def get_all_farmers(self, skip: int = 0, limit: int = 100) -> List[Farmer]:
        """Get all farmers with pagination."""
        result = await self.db.execute(
            select(Farmer)
            .options(selectinload(Farmer.user))
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
