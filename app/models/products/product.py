from sqlalchemy import Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from typing import Optional
from app.models.base import Base


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    stock: Mapped[int] = mapped_column(Integer, default=0)
    seasonal_availability: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    category_id: Mapped[int] = mapped_column(
        ForeignKey("product_categories.id"), nullable=False
    )
    farmer_id: Mapped[int] = mapped_column(ForeignKey("farmers.id"), nullable=False)

    category = relationship("ProductCategory", back_populates="products")
    farmer = relationship("Farmer", back_populates="products")
