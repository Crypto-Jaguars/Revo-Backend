"""
Location model for storing geographical coordinates and address information.
"""

from sqlalchemy import Float, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.farmers.farmer import Farmer


class Location(Base):
    """Location model for storing address and coordinates."""

    __tablename__ = "locations"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    address: Mapped[str] = mapped_column(String(255), nullable=True)
    city: Mapped[str] = mapped_column(String(100), nullable=True)
    state: Mapped[str] = mapped_column(String(100), nullable=True)
    country: Mapped[str] = mapped_column(String(100), nullable=True)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)

    # Reverse relation added in Farmer model
    farmer: Mapped["Farmer"] = relationship("Farmer", back_populates="location", uselist=False) 