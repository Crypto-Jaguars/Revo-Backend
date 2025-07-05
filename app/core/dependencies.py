"""
FastAPI dependencies for authentication and authorization.
"""
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel

from app.core.security import verify_token, TokenData

# OAuth2 scheme for bearer token
security = HTTPBearer(auto_error=False)


class CurrentUser(BaseModel):
    """Current user model for authenticated requests."""
    id: str
    username: str
    email: Optional[str] = None
    is_active: bool = True


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> CurrentUser:
    """
    Get the current authenticated user from JWT token.
    
    Args:
        credentials: HTTP Authorization credentials from bearer token
        
    Returns:
        CurrentUser instance with user information
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = credentials.credentials
    token_data = verify_token(token, credentials_exception)
    
    # In a real application, you would fetch the user from the database
    # For now, we'll create a mock user based on token data
    if token_data.username is None:
        raise credentials_exception
    
    # TODO: Replace with actual database lookup
    # user = await get_user_by_username(token_data.username)
    # if user is None:
    #     raise credentials_exception
    
    # Mock user creation for testing
    current_user = CurrentUser(
        id="1",
        username=token_data.username,
        email=f"{token_data.username}@example.com",
        is_active=True
    )
    
    return current_user


async def get_current_active_user(
    current_user: CurrentUser = Depends(get_current_user)
) -> CurrentUser:
    """
    Get the current active user (must be active).
    
    Args:
        current_user: The current user from get_current_user dependency
        
    Returns:
        CurrentUser instance if user is active
        
    Raises:
        HTTPException: If user is inactive
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Inactive user"
        )
    return current_user


def get_optional_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[CurrentUser]:
    """
    Get the current user if authenticated, otherwise return None.
    Useful for endpoints that work with or without authentication.
    
    Args:
        credentials: Optional HTTP Authorization credentials
        
    Returns:
        CurrentUser instance if authenticated, None otherwise
    """
    if not credentials:
        return None
    
    try:
        token_data = verify_token(
            credentials.credentials, 
            HTTPException(status_code=401)
        )
        
        if token_data.username is None:
            return None
        
        # TODO: Replace with actual database lookup
        return CurrentUser(
            id="1",
            username=token_data.username,
            email=f"{token_data.username}@example.com",
            is_active=True
        )
    except Exception:
        return None
