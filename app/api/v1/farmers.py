from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.auth import get_current_user  # Import your authentication dependency
from app.schemas.farmer import FarmerCreate, FarmerUpdate, FarmerResponse
from app.schemas.user import User  # Import your User schema/model
from app.services.farmer_service import FarmerService

router = APIRouter()

@router.post("/", response_model=FarmerResponse, status_code=status.HTTP_201_CREATED)
async def create_farmer_profile(
    user_id: int,
    farmer_data: FarmerCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)  # Add authentication
):
    """Create a new farmer profile."""
    # Authorization check
    if current_user.id != user_id and not getattr(current_user, "is_admin", False):
        raise HTTPException(status_code=403, detail="Not authorized to create profile for this user")
    farmer_service = FarmerService(db)
    try:
        farmer = await farmer_service.create_farmer_profile(user_id, farmer_data)
        return farmer
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

@router.get("/{farmer_id}", response_model=FarmerResponse)
async def get_farmer(
    farmer_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get farmer by ID."""
    farmer_service = FarmerService(db)
    farmer = await farmer_service.get_farmer_by_id(farmer_id)
    if not farmer:
        raise HTTPException(status_code=404, detail="Farmer not found")
    return farmer

@router.get("/user/{user_id}", response_model=FarmerResponse)
async def get_farmer_by_user(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get farmer by user ID."""
    farmer_service = FarmerService(db)
    farmer = await farmer_service.get_farmer_by_user_id(user_id)
    if not farmer:
        raise HTTPException(status_code=404, detail="Farmer profile not found for this user")
    return farmer

@router.put("/{farmer_id}", response_model=FarmerResponse)
async def update_farmer(
    farmer_id: int,
    farmer_data: FarmerUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update farmer profile."""
    farmer_service = FarmerService(db)
    farmer = await farmer_service.update_farmer_profile(farmer_id, farmer_data)
    if not farmer:
        raise HTTPException(status_code=404, detail="Farmer not found")
    return farmer

@router.delete("/{farmer_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_farmer(
    farmer_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete farmer profile."""
    farmer_service = FarmerService(db)
    success = await farmer_service.delete_farmer_profile(farmer_id)
    if not success:
        raise HTTPException(status_code=404, detail="Farmer not found")

@router.get("/", response_model=List[FarmerResponse])
async def list_farmers(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """List all farmers with pagination."""
    farmer_service = FarmerService(db)
    farmers = await farmer_service.get_all_farmers(skip=skip, limit=limit)
    return farmers
