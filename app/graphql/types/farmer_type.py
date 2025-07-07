import strawberry
from typing import Optional


@strawberry.type
class FarmerType:
    id: int
    name: str
    email: str
    phone: Optional[str]
    location: Optional[str]
    verified: bool
