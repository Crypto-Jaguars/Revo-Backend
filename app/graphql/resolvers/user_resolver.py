import strawberry
from app.services import user_service
from app.graphql.types.user_type import UserType
from typing import Optional

@strawberry.type
class Query:
    @strawberry.field
    async def user(self, id: int, info) -> Optional[UserType]:
        db = info.context["db"]
        user = await user_service.get_user_by_id(db, id)
        if user:
            return UserType(
                id=user.id,
                email=user.email,
                user_type=user.user_type.value if hasattr(user.user_type, "value") else user.user_type,
                is_active=user.is_active,
            )
        return None

    @strawberry.field
    async def current_user(self, info) -> Optional[UserType]:
        db = info.context["db"]
        user = await user_service.get_current_user(info.context["request"], db)
        if user:
            return UserType(
                id=user.id,
                email=user.email,
                user_type=user.user_type.value if hasattr(user.user_type, "value") else user.user_type,
                is_active=user.is_active,
            )
        return None 