from sqlalchemy import String
from sqlalchemy.orm import relationship, Mapped, mapped_column
from typing import Optional
from app.models.base import Base


class ProductCategory(Base):
    __tablename__ = "product_categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    description: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    products = relationship("Product", back_populates="category")
