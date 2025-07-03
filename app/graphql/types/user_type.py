import strawberry
from typing import Optional

@strawberry.type
class UserType:
    id: int
    email: str
    user_type: str
    is_active: bool 