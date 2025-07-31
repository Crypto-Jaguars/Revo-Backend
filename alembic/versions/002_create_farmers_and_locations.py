"""create farmers and locations tables

Revision ID: 004
Revises: 
Create Date: 2025-07-31
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create locations table first
    op.create_table(
        "locations",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("address", sa.String(length=255), nullable=True),
        sa.Column("city", sa.String(length=100), nullable=True),
        sa.Column("state", sa.String(length=100), nullable=True),
        sa.Column("country", sa.String(length=100), nullable=True),
        sa.Column("latitude", sa.Float, nullable=False),
        sa.Column("longitude", sa.Float, nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), onupdate=sa.func.now()),
    )
    
    # Create farmers table with location_id foreign key
    op.create_table(
        "farmers",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False, unique=True),
        sa.Column("farm_name", sa.String(length=255), nullable=False),
        sa.Column("farm_size", sa.Float, nullable=True),
        sa.Column("location_id", sa.Integer(), sa.ForeignKey("locations.id"), nullable=True),
        sa.Column("organic_certified", sa.Boolean, nullable=False, server_default=sa.text("false")),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), onupdate=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("farmers")
    op.drop_table("locations") 