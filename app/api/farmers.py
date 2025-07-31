"""
Farmers REST API endpoints for Farmers Marketplace.

Provides CRUD operations for farmer profiles, location-based search,
and farmer verification endpoints.
"""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_active_user, CurrentUser
from app.schemas.farmer import FarmerCreate, FarmerUpdate, FarmerResponse
from app.services.farmer_service import FarmerService

router = APIRouter()


@router.get("/", response_model=List[FarmerResponse])
async def list_farmers(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    db: AsyncSession = Depends(get_db)
) -> List[FarmerResponse]:
    """
    Get list of all farmers with pagination.
    
    Args:
        skip: Number of records to skip for pagination
        limit: Maximum number of records to return
        db: Database session
        
    Returns:
        List of farmer profiles
    """
    farmers = await FarmerService.get_all(db)
    # Apply pagination
    paginated_farmers = farmers[skip:skip + limit]
    return [FarmerResponse.model_validate(farmer) for farmer in paginated_farmers]


@router.get("/{farmer_id}", response_model=FarmerResponse)
async def get_farmer(
    farmer_id: UUID,
    db: AsyncSession = Depends(get_db)
) -> FarmerResponse:
    """
    Get a specific farmer by ID.
    
    Args:
        farmer_id: UUID of the farmer
        db: Database session
        
    Returns:
        Farmer profile data
        
    Raises:
        HTTPException: If farmer not found
    """
    farmer = await FarmerService.get_by_id(db, farmer_id)
    if not farmer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Farmer not found"
        )
    return FarmerResponse.model_validate(farmer)


@router.post("/", response_model=FarmerResponse, status_code=status.HTTP_201_CREATED)
async def create_farmer(
    data: FarmerCreate,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_active_user)
) -> FarmerResponse:
    """
    Create a new farmer profile.
    
    Args:
        data: Farmer creation data
        db: Database session
        current_user: Authenticated user
        
    Returns:
        Created farmer profile
        
    Raises:
        HTTPException: If user tries to create profile for another user
    """
    # Ensure user can only create profile for themselves
    if current_user.id != str(data.user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot create profile for another user"
        )
    
    # Check if user already has a farmer profile
    existing_farmer = await FarmerService.get_by_user_id(db, data.user_id)
    if existing_farmer:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already has a farmer profile"
        )
    
    farmer = await FarmerService.create(db, data)
    return FarmerResponse.model_validate(farmer)


@router.put("/{farmer_id}", response_model=FarmerResponse)
async def update_farmer(
    farmer_id: UUID,
    data: FarmerUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_active_user)
) -> FarmerResponse:
    """
    Update an existing farmer profile.
    
    Args:
        farmer_id: UUID of the farmer to update
        data: Updated farmer data
        db: Database session
        current_user: Authenticated user
        
    Returns:
        Updated farmer profile
        
    Raises:
        HTTPException: If farmer not found or user not authorized
    """
    farmer = await FarmerService.get_by_id(db, farmer_id)
    if not farmer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Farmer not found"
        )
    
    # Ensure user can only update their own profile
    if str(farmer.user_id) != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this profile"
        )
    
    farmer = await FarmerService.update(db, farmer, data)
    return FarmerResponse.model_validate(farmer)


@router.delete("/{farmer_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_farmer(
    farmer_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_active_user)
) -> None:
    """
    Delete a farmer profile.
    
    Args:
        farmer_id: UUID of the farmer to delete
        db: Database session
        current_user: Authenticated user
        
    Raises:
        HTTPException: If farmer not found or user not authorized
    """
    farmer = await FarmerService.get_by_id(db, farmer_id)
    if not farmer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Farmer not found"
        )
    
    # Ensure user can only delete their own profile
    if str(farmer.user_id) != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this profile"
        )
    
    await FarmerService.delete(db, farmer)


@router.get("/search/location/", response_model=List[FarmerResponse])
async def search_farmers_by_location(
    lat: float = Query(..., description="Latitude of search center"),
    lng: float = Query(..., description="Longitude of search center"),
    radius: float = Query(50.0, ge=0.1, le=500.0, description="Search radius in kilometers"),
    db: AsyncSession = Depends(get_db)
) -> List[FarmerResponse]:
    """
    Search for farmers within a specified radius of given coordinates.
    
    Args:
        lat: Latitude of search center
        lng: Longitude of search center
        radius: Search radius in kilometers (0.1 to 500 km)
        db: Database session
        
    Returns:
        List of farmers within the specified radius
    """
    farmers = await FarmerService.search_by_location(db, lat, lng, radius)
    return [FarmerResponse.model_validate(farmer) for farmer in farmers]


@router.get("/search/name/", response_model=List[FarmerResponse])
async def search_farmers_by_name(
    farm_name: str = Query(..., min_length=1, description="Farm name to search for"),
    db: AsyncSession = Depends(get_db)
) -> List[FarmerResponse]:
    """
    Search for farmers by farm name (case-insensitive partial match).
    
    Args:
        farm_name: Farm name to search for
        db: Database session
        
    Returns:
        List of farmers matching the search criteria
    """
    farmers = await FarmerService.search_by_farm_name(db, farm_name)
    return [FarmerResponse.model_validate(farmer) for farmer in farmers]


@router.get("/organic/", response_model=List[FarmerResponse])
async def get_organic_farmers(
    db: AsyncSession = Depends(get_db)
) -> List[FarmerResponse]:
    """
    Get all organic certified farmers.
    
    Args:
        db: Database session
        
    Returns:
        List of organic certified farmers
    """
    farmers = await FarmerService.get_organic_farmers(db)
    return [FarmerResponse.model_validate(farmer) for farmer in farmers]


@router.get("/me/profile", response_model=FarmerResponse)
async def get_my_farmer_profile(
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_active_user)
) -> FarmerResponse:
    """
    Get the current user's farmer profile.
    
    Args:
        db: Database session
        current_user: Authenticated user
        
    Returns:
        Current user's farmer profile
        
    Raises:
        HTTPException: If user doesn't have a farmer profile
    """
    farmer = await FarmerService.get_by_user_id(db, UUID(current_user.id))
    if not farmer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No farmer profile found for current user"
        )
    return FarmerResponse.model_validate(farmer) 