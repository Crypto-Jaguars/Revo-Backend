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
    
    # Fetch user from database using email (username in token)
    from app.services.auth_service import auth_service
    from app.core.database import get_db
    
    async for db in get_db():
        user = await auth_service.get_user_by_email(db, token_data.username)
        if user is None:
            raise credentials_exception
        
        current_user = CurrentUser(
            id=str(user.id),
            username=user.email,
            email=user.email,
            is_active=user.is_active
        )
        break
    
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


async def get_optional_current_user(
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
        
        # Fetch user from database using email
        from app.services.auth_service import auth_service
        from app.core.database import get_db
        
        async for db in get_db():
            user = await auth_service.get_user_by_email(db, token_data.username)
            if user is None:
                return None
            
            return CurrentUser(
                id=str(user.id),
                username=user.email,
                email=user.email,
                is_active=user.is_active
            )
    except Exception:
        return None
