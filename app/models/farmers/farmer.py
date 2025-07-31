from sqlalchemy import Boolean, Column, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from uuid import UUID
from typing import TYPE_CHECKING
import uuid

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.users.user import User

class Farmer(Base):
    __tablename__ = "farmers"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), unique=True, nullable=False)
    farm_name: Mapped[str] = mapped_column(String(255), nullable=False)
    farm_size: Mapped[float] = mapped_column(nullable=True)
    location: Mapped[str] = mapped_column(String(255), nullable=True)
    organic_certified: Mapped[bool] = mapped_column(Boolean, default=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="farmer") 