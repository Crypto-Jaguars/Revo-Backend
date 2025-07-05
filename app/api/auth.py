"""
Authentication API routes.
"""
from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel

from app.core.dependencies import CurrentUser, get_current_active_user
from app.core.security import (
    Token,
    create_token_for_user,
    get_password_hash,
    verify_password,
)

router = APIRouter()


class UserLogin(BaseModel):
    """User login request model."""
    username: str
    password: str


class UserRegister(BaseModel):
    """User registration request model."""
    username: str
    email: str
    password: str
    full_name: str = ""


class UserResponse(BaseModel):
    """User response model."""
    id: str
    username: str
    email: str
    full_name: str
    is_active: bool


# Mock user database - replace with actual database operations
MOCK_USERS = {
    "testuser": {
        "id": "1",
        "username": "testuser",
        "email": "test@example.com",
        "full_name": "Test User",
        "hashed_password": get_password_hash("testpass123"),
        "is_active": True,
    }
}


def authenticate_user(username: str, password: str) -> dict | None:
    """
    Authenticate a user with username and password.
    
    Args:
        username: The username
        password: The plain text password
        
    Returns:
        User dict if authentication successful, None otherwise
    """
    user = MOCK_USERS.get(username)
    if not user:
        return None
    if not verify_password(password, user["hashed_password"]):
        return None
    return user


@router.post("/login", response_model=Token)
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    """
    OAuth2 compatible token login, get an access token for future requests.
    """
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_token_for_user(
        user_id=user["id"],
        username=user["username"]
    )
    
    return Token(access_token=access_token, token_type="bearer")


@router.post("/login/json", response_model=Token)
async def login_json(user_data: UserLogin):
    """
    JSON login endpoint - alternative to OAuth2 form login.
    """
    user = authenticate_user(user_data.username, user_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    
    access_token = create_token_for_user(
        user_id=user["id"],
        username=user["username"]
    )
    
    return Token(access_token=access_token, token_type="bearer")


@router.post("/register", response_model=UserResponse)
async def register(user_data: UserRegister):
    """
    Register a new user.
    """
    # Check if username already exists
    if user_data.username in MOCK_USERS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Check if email already exists
    for user in MOCK_USERS.values():
        if user["email"] == user_data.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    new_user_id = str(len(MOCK_USERS) + 1)
    
    new_user = {
        "id": new_user_id,
        "username": user_data.username,
        "email": user_data.email,
        "full_name": user_data.full_name,
        "hashed_password": hashed_password,
        "is_active": True,
    }
    
    MOCK_USERS[user_data.username] = new_user
    
    return UserResponse(
        id=new_user["id"],
        username=new_user["username"],
        email=new_user["email"],
        full_name=new_user["full_name"],
        is_active=new_user["is_active"]
    )


@router.get("/me", response_model=UserResponse)
async def read_users_me(
    current_user: CurrentUser = Depends(get_current_active_user)
):
    """
    Get current user information.
    """
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email or f"{current_user.username}@example.com",
        full_name=f"User {current_user.username}",
        is_active=current_user.is_active
    )


@router.get("/protected")
async def protected_route(
    current_user: CurrentUser = Depends(get_current_active_user)
):
    """
    Example protected route that requires authentication.
    """
    return {
        "message": f"Hello {current_user.username}! This is a protected route.",
        "user_id": current_user.id,
        "timestamp": "2025-07-03T12:00:00Z"
    }
