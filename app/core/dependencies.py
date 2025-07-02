from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import verify_access_token
from app.core.database import get_db
from typing import Any, Optional

# TODO: Replace with actual user model import
# from app.models.users import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    try:
        payload = verify_access_token(token)
        user_id: Optional[int] = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload.")
        # TODO: Implement actual user lookup once User model is available
        # user = await db.get(User, user_id)
        # if not user:
        #     raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found.")
        user = {"id": user_id}  # Placeholder – remove when real user lookup is implemented
        return user
    except ValueError as e:
        # Handle token verification errors from verify_access_token
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials."
        ) from e
    except Exception as e:
        # Handle unexpected errors
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials."
        ) from e 