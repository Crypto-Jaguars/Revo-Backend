from datetime import datetime, timedelta
from typing import Any
from jose import jwt, JWTError
from app.core.config import get_settings

ALGORITHM = get_settings().algorithm


def create_access_token(data: dict[str, Any], expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=get_settings().access_token_expire_minutes))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, get_settings().secret_key, algorithm=ALGORITHM)
    return encoded_jwt


def verify_access_token(token: str) -> dict[str, Any]:
    try:
        payload = jwt.decode(token, get_settings().secret_key, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise ValueError("Invalid token or expired token.") 